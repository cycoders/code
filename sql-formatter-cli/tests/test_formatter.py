'''Formatter tests.''' 

import pytest
from sql_formatter_cli.formatter import format_sql
from sql_formatter_cli.config import DEFAULTS


@pytest.mark.parametrize(
    "dialect, input_sql, expected",
    [
        (
            "postgres",
            "select * from users where id=1",
            "SELECT *\n  FROM users\n  WHERE id = 1",
        ),
        (
            "mysql",
            "select @@version",
            "SELECT @@VERSION",
        ),
        (
            "sqlite",
            "PRAGMA table_info(users);",
            "PRAGMA table_info(users)",
        ),
        # Multi-statement
        (
            "postgres",
            "select 1; select 2",
            "SELECT 1\n\nSELECT 2",
        ),
    ],
)
def test_format_sql(dialect: str, input_sql: str, expected: str, default_config):
    config = DEFAULTS.copy()
    config["dialect"] = dialect
    assert format_sql(input_sql, config) == expected


def test_adjust_indent(default_config):
    config = default_config.copy()
    config["indent"] = "    "
    sql = "SELECT *\n    FROM t"
    # Simulate post-process input
    from sql_formatter_cli.utils import adjust_indent
    adjusted = adjust_indent(sql, config["indent"])
    assert adjusted == "SELECT *\n        FROM t"


def test_keyword_case_lower(default_config):
    config = default_config.copy()
    config["keyword_case"] = "lower"
    sql = format_sql("SELECT * FROM t", config)
    assert "select" in sql.lower()


def test_invalid_sql():
    with pytest.raises(ValueError, match="Invalid SQL"):
        format_sql("invalid", {"dialect": "postgres"})


def test_empty_sql():
    assert format_sql("", {"dialect": "postgres"}) == ""
