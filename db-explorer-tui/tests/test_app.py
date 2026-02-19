import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from db_explorer_tui.app import DBExplorer


@pytest.mark.asyncio
async def test_load_schema_calls_db_methods(mocker):
    mock_db = AsyncMock()
    mock_db.get_tables.return_value = ["test_table"]
    mock_db.get_columns.return_value = ["id", "name"]
    mocker.patch("db_explorer_tui.app.DBManager", return_value=mock_db)

    app = DBExplorer(dsn="sqlite:///:memory:")
    await app._init_db()
    await app.load_schema()

    mock_db.get_tables.assert_called_once()
    mock_db.get_columns.assert_called()


@pytest.mark.asyncio
@patch("db_explorer_tui.app.DBManager")
async def test_init_db_handles_error(mock_db_class: MagicMock):
    mock_db_class.side_effect = Exception("Connection failed")
    app = DBExplorer()
    with pytest.raises(Exception):
        await app._init_db()


@pytest.mark.parametrize(
    "query,expected_rowcount",
    [
        ("SELECT COUNT(*) FROM users", 2),
        ("SELECT name FROM users", 2),
    ],
)
@pytest.mark.asyncio
async def test_run_query(sqlite_manager, query: str, expected_rowcount: int, mocker):
    # Note: app integration mocked
    mock_app = MagicMock()
    mock_app.db_manager.execute.return_value = [{"count": expected_rowcount}] if "COUNT" in query else [{"name": "test"}] * expected_rowcount
    mocker.patch("db_explorer_tui.app.DBExplorer.notify")
    # Simplified test
    results = await sqlite_manager.execute(query)
    assert len(results) == expected_rowcount