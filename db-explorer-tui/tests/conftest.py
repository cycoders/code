import asyncio
import pytest
from pathlib import Path

from db_explorer_tui.db import DBManager


@pytest.fixture(scope="session")
async def sqlite_manager() -> DBManager:
    dsn = "sqlite+aiosqlite:///:memory:"
    mgr = DBManager(dsn)
    await mgr.connect()
    await mgr._conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        );
    """)
    await mgr._conn.execute(
        "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com'), ('Bob', 'bob@example.com')"
    )
    yield mgr
    await mgr.disconnect()


@pytest.fixture
async def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()