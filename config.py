"""Конфигурация бота. Все значения берутся из переменных окружения (.env)."""
import os
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def _get(name: str, default: str = "") -> str:
    value = os.getenv(name)
    return value if value is not None else default


def _get_int(name: str, default: int) -> int:
    try:
        return int(_get(name, str(default)))
    except (TypeError, ValueError):
        return default


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on", "y"}


@dataclass(frozen=True)
class ParserConfig:
    """Настройки парсера Excel.

    Каждое поле COL_* может быть:
      * int  — 0-based индекс колонки (если файл без строки-шапки);
      * str  — точное/частичное название колонки в шапке;
      * None — авто-определение по синонимам (см. *_SYNONYMS).

    COL_DAY оставлен для будущих форматов, где внутри одного листа несколько
    дней; сейчас дата берётся из имени папки на Яндекс.Диске.
    """
    COL_DAY: Optional[object] = None
    COL_LESSON_NUM: Optional[object] = None
    COL_TIME: Optional[object] = None
    COL_SUBJECT: Optional[object] = None
    COL_ROOM: Optional[object] = None

    DAY_SYNONYMS: tuple = ("день", "дата", "day")
    LESSON_NUM_SYNONYMS: tuple = ("пара", "№", "номер", "номер пары", "№ пары", "lesson")
    TIME_SYNONYMS: tuple = ("время", "время пары", "часы", "time")
    SUBJECT_SYNONYMS: tuple = ("предмет", "дисциплина", "предмет/дисциплина", "название", "subject")
    ROOM_SYNONYMS: tuple = ("кабинет", "каб", "ауд", "аудитория", "ауд.", "room")

    # Regex названия группы: "1ОГР-26-9", "БУХ-26-9", "ОПИр-25-9", "ОГР-23".
    GROUP_NAME_PATTERN: str = r"^[А-Яа-яЁёA-Za-z0-9]+-\d{2,4}(-\d+)?$"

    # Сколько первых строк листа проверять при поиске строки-шапки.
    HEADER_SCAN_ROWS: int = 6


@dataclass(frozen=True)
class Settings:
    BOT_TOKEN: str = field(default_factory=lambda: _get("BOT_TOKEN"))
    DATABASE_URL: str = field(default_factory=lambda: _get("DATABASE_URL"))
    ADMIN_ID: int = field(default_factory=lambda: _get_int("ADMIN_ID", 0))
    POLL_INTERVAL_MINUTES: int = field(default_factory=lambda: _get_int("POLL_INTERVAL_MINUTES", 3))
    YADISK_PUBLIC_URL: str = field(default_factory=lambda: _get("YADISK_PUBLIC_URL"))
    SUBFOLDER_NAME: str = field(default_factory=lambda: _get("SUBFOLDER_NAME", "студентам"))
    TZ_NAME: str = field(default_factory=lambda: _get("TZ_NAME", "Asia/Novosibirsk"))
    REQUEST_TIMEOUT: float = field(default_factory=lambda: float(_get("REQUEST_TIMEOUT", "15")))
    REQUEST_RETRIES: int = field(default_factory=lambda: _get_int("REQUEST_RETRIES", 3))
    BROADCAST_DELAY_MS: int = field(default_factory=lambda: _get_int("BROADCAST_DELAY_MS", 50))
    SHOW_TIME: bool = field(default_factory=lambda: _get_bool("SHOW_TIME", False))
    parser: ParserConfig = field(default_factory=ParserConfig)


settings = Settings()
