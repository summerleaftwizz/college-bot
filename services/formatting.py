"""Форматирование расписания в HTML-текст для Telegram."""
import html

from config import settings


def esc(value) -> str:
    return html.escape(str(value), quote=False)


def _lesson_line(lesson) -> str:
    n = lesson.lesson_number
    if not lesson.subject:
        return f"🕐 {n} парой — ничего"
    if settings.SHOW_TIME and lesson.time:
        if lesson.room:
            return f"🕐 {n} парой ({esc(lesson.time)}) — {esc(lesson.subject)} (каб. {esc(lesson.room)})"
        return f"🕐 {n} парой ({esc(lesson.time)}) — {esc(lesson.subject)}"
    if lesson.room:
        return f"🕐 {n} парой — {esc(lesson.subject)} (каб. {esc(lesson.room)})"
    return f"🕐 {n} парой — {esc(lesson.subject)}"


def format_schedule(
    date_label: str,
    group: str,
    lessons,
    empty_text: str = "Сегодня пар нет 🎉",
    title: str | None = None,
) -> str:
    header = title or f"📅 Расписание на {esc(date_label)} ({esc(group)})"
    if not lessons:
        return f"{header}\n{empty_text}"
    lines = [header]
    for lesson in sorted(lessons, key=lambda l: l.lesson_number):
        lines.append(_lesson_line(lesson))
    return "\n".join(lines)


def format_notification(date_label: str, group: str, lessons) -> str:
    return (
        f"📅 Появилось новое расписание на {esc(date_label)}!\n\n"
        + format_schedule(date_label, group, lessons)
    )
