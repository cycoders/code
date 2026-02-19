import pytest
from typing import List

from db_explorer_tui.db import DBManager


@pytest.mark.asyncio
async def test_connect_sqlite(sqlite_manager: DBManager) -> None:
    assert sqlite_manager._conn is not None


@pytest.mark.asyncio
async def test_get_tables_sqlite(sqlite_manager: DBManager) -> None:
    tables: List[str] = await sqlite_manager.get_tables()
    assert "users" in tables


@pytest.mark.asyncio
async def test_get_columns_sqlite(sqlite_manager: DBManager) -> None:
    columns = await sqlite_manager.get_columns("users")
    assert "id" in columns
    assert "name" in columns
    assert "email" in columns


@pytest.mark.asyncio
async def test_execute_sqlite(sqlite_manager: DBManager) -> None:
    results = await sqlite_manager.execute("SELECT * FROM users")
    assert len(results) == 2
    assert results[0]["name"] == "Alice"


@pytest.mark.asyncio
async def test_execute_error_handling(sqlite_manager: DBManager) -> None:
    with pytest.raises(databases.exceptions.ExecutionError):
        await sqlite_manager.execute("SELECT * FROM nonexistent")


@pytest.mark.asyncio
async def test_disconnect(sqlite_manager: DBManager) -> None:
    await sqlite_manager.disconnect()
    assert sqlite_manager._conn is None