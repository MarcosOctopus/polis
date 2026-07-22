"""Database connection and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import settings

if settings.use_sqlite:
    # ── SQLite (dev) — single connection, no pooling ────────────────────────
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False},
        poolclass=None,  # disable pooling for SQLite
    )
else:
    # ── PostgreSQL (production) ─────────────────────────────────────────────
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async DB session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
