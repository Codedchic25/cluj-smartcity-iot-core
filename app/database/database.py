# app/database/database.py
"""Database orchestration, connection pooling, and maintenance for Smart City Cluj-Napoca."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# -------------------------------------------------------------------------
# DATABASE CONFIGURATION LAYER (HYBRID ENGINE: CLOUD POSTGRESQL / LOCAL SQLITE)
# -------------------------------------------------------------------------

# Detectăm dacă Railway ne-a injectat variabila de producție pentru PostgreSQL
DATABASE_URL_ENV = os.getenv("DATABASE_URL")

if DATABASE_URL_ENV:
    # Pentru SQLAlchemy asincron, înlocuim protocolul clasic cu cel compatibil asyncpg
    if DATABASE_URL_ENV.startswith("postgresql://"):
        ASYNC_DATABASE_URL = DATABASE_URL_ENV.replace("postgresql://", "postgresql+asyncpg://")
    else:
        ASYNC_DATABASE_URL = DATABASE_URL_ENV
    
    # Configurație optimizată pentru PostgreSQL în producție pe Railway
    async_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
else:
    # Cale relativă inteligentă care se adaptează pe orice PC (evită căile absolute fixe)
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATABASE_PATH = BASE_DIR / "app.db"
    ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"
    
    # Configurație izolată cu parametri de siguranță pentru SQLite local
    async_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )

# Fabrica centrală de sesiuni asincrone
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# -------------------------------------------------------------------------
# CONTEXT MANAGERS & DATABASE OPERATIONS
# -------------------------------------------------------------------------

@asynccontextmanager
async def get_async_db_session():
    """Context manager asincron enterprise pentru garantarea închiderii conexiunilor."""
    session: AsyncSession = async_session_factory()
    try:
        yield session
    finally:
        await session.close()


async def get_alert_thresholds_async() -> tuple[float, float, float, float]:
    """Retrieve active system safety thresholds from the persistent settings layer."""
    query = "SELECT temp_limit, noise_limit, air_limit, soil_limit FROM settings WHERE id = 1"
    try:
        async with get_async_db_session() as session:
            result = await session.execute(text(query))
            row = result.fetchone()
            if row:
                return (float(row[0]), float(row[1]), float(row[2]), float(row[3]))
    except Exception as exc:
        print(
            f"⚠️ [DATABASE] Eșec la încărcarea setărilor din baza de date, se folosesc valorile implicite: {exc}"
        )

    return (32.0, 75.0, 80.0, 35.0)


async def cleanup_old_data(hours: int = 24) -> None:
    """Enterprise-grade asynchronous maintenance loop to purge data older than retention thresholds."""
    limit_time = datetime.now(UTC) - timedelta(hours=hours)
    limit_time_str = limit_time.strftime("%Y-%m-%d %H:%M:%S")

    async with get_async_db_session() as session:
        try:
            await session.execute(
                text("DELETE FROM city_stats WHERE timestamp < :limit_time"),
                {"limit_time": limit_time_str},
            )
            await session.commit()
            print(
                f"🧹 [DATABASE MAINTENANCE] Datele mai vechi de {hours} ore au fost șterse controlat."
            )
        except Exception as exc:
            await session.rollback()
            print(f"❌ [DATABASE MAINTENANCE] Purjarea datelor istorice a eșuat: {exc}")
