import pytest
from pathlib import Path
from db_migration_auditor.linter import lint_file
from db_migration_auditor.models import Dialect
from sqlglot.dialects import Dialects


@pytest.fixture
def drop_table_sql(tmp_path: Path) -> Path:
    p = tmp_path / "drop.sql"
    p.write_text("DROP TABLE users;")
    return p


def test_lint_file(drop_table_sql: Path):
    issues = lint_file(str(drop_table_sql), Dialects.POSTGRES)
    assert len(issues) == 1
    assert issues[0].code == "no_drop_table"


def test_parse_error(tmp_path: Path):
    broken = tmp_path / "broken.sql"
    broken.write_text("SELECT * FROM invalid syntax")
    issues = lint_file(str(broken), Dialects.SQLITE)
    assert any(i.code == "parse_error" for i in issues)