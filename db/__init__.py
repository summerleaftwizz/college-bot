from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings
from db.base import Base
from db import models  # noqa: F401  — регистрирует модели в Base.metadata


def _normalize_database_url(url: str) -> str:
    """Приводит DATABASE_URL к асинхронному драйверу asyncpg.

    Railway/Amvera часто выдают URL вида 'postgresql://...' (без +asyncpg),
    а create_async_engine требует 'postgresql+asyncpg://...'.
    """
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+asyncpg://" + url[len(prefix):]
    return url


engine = create_async_engine(
    _normalize_database_url(settings.DATABASE_URL), echo=False, pool_pre_ping=True
)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Создаёт таблицы, если их ещё нет, и применяет миграции схемы."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_migrate_schema)


def _migrate_schema(sync_conn) -> None:
    """Исправляет устаревшую схему SQLite.

    Раньше users.id был BIGINT, а SQLite автоинкрементит только INTEGER
    PRIMARY KEY, из-за чего INSERT падал с "NOT NULL constraint failed:
    users.id". Если таблица users осталась со старым типом — пересоздаём её.
    Таблица при этом пустая: все прежние вставки не проходили.
    """
    if sync_conn.dialect.name != "sqlite":
        return
    # PRAGMA table_info(users) -> (cid, name, type, notnull, dflt_value, pk)
    rows = sync_conn.exec_driver_sql("PRAGMA table_info(users)").fetchall()
    id_col = next((r for r in rows if r[1] == "id"), None)
    if id_col is None or str(id_col[2]).upper() != "BIGINT":
        return
    sync_conn.exec_driver_sql("DROP TABLE users")
    models.User.__table__.create(sync_conn)


async def dispose_db() -> None:
    await engine.dispose()
