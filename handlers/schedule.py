import logging

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

from db import SessionLocal
from db import crud
from keyboards.groups import build_groups_keyboard
from services import formatting, watcher
from utils import today_ddmm, tomorrow_ddmm, week_days

logger = logging.getLogger(__name__)
router = Router()


async def _get_group(telegram_id: int) -> str | None:
    async with SessionLocal() as session:
        user = await crud.get_user(session, telegram_id)
        return user.group if user else None


async def _require_group(message: Message) -> str | None:
    group = await _get_group(message.from_user.id)
    if not group:
        await message.answer("Сначала выбери группу: /start")
    return group


async def _load(date: str, group: str):
    async with SessionLocal() as session:
        return await crud.get_schedule(session, date, group)


@router.message(Command("today"))
async def cmd_today(message: Message, bot: Bot) -> None:
    group = await _require_group(message)
    if not group:
        return
    label = today_ddmm()
    entries = await _load(label, group)
    if not entries:
        await message.answer("Заглядываю на Яндекс.Диск…")
        try:
            await watcher.run_check(bot)
        except Exception:
            logger.exception("ошибка принудительной загрузки расписания")
        entries = await _load(label, group)

    text = formatting.format_schedule(label, group, entries, empty_text="Сегодня пар нет 🎉")
    await message.answer(text, parse_mode="HTML")


@router.message(Command("tomorrow"))
async def cmd_tomorrow(message: Message) -> None:
    group = await _require_group(message)
    if not group:
        return
    label = tomorrow_ddmm()
    entries = await _load(label, group)
    text = formatting.format_schedule(label, group, entries, empty_text="Завтра пар нет 🎉")
    await message.answer(text, parse_mode="HTML")


@router.message(Command("week"))
async def cmd_week(message: Message) -> None:
    group = await _require_group(message)
    if not group:
        return
    for day_name, label in week_days():
        entries = await _load(label, group)
        title = f"📅 {day_name} ({label}) — {group}"
        text = formatting.format_schedule(label, group, entries, empty_text="Пар нет 🎉", title=title)
        await message.answer(text, parse_mode="HTML")


@router.message(Command("change_group"))
async def cmd_change_group(message: Message) -> None:
    async with SessionLocal() as session:
        groups = await crud.get_groups(session)
    if not groups:
        await message.answer("Расписание ещё не загружено, групп пока нет. Попробуй позже.")
        return
    await message.answer("Выбери группу:", reply_markup=build_groups_keyboard(groups))


@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message) -> None:
    async with SessionLocal() as session:
        await crud.set_subscribed(session, message.from_user.id, True)
        await session.commit()
    await message.answer("Автоуведомления включены ✅")


@router.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: Message) -> None:
    async with SessionLocal() as session:
        await crud.set_subscribed(session, message.from_user.id, False)
        await session.commit()
    await message.answer("Автоуведомления выключены 🔕")
