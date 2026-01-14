'''Config loading tests.''' 

import os
import pytest
from tempfile import NamedTemporaryFile
from sql_formatter_cli.config import load_config, DEFAULTS


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv("SQLFMT_DIALECT", raising=False)


def test_defaults():
    assert load_config() == DEFAULTS


def test_file_config(tmp_path):
    config_file = tmp_path / ".sqlformatter.toml"
    config_file.write_text('dialect = "mysql"\nline_length = 120')
    config = load_config(str(config_file))
    assert config["dialect"] == "mysql"
    assert config["line_length"] == 120


def test_env_override(monkeypatch):
    monkeypatch.setenv("SQLFMT_DIALECT", "sqlite")
    config = load_config()
    assert config["dialect"] == "sqlite"


def test_cli_override():
    config = load_config(overrides={"line_length": 80})
    assert config["line_length"] == 80


def test_pyproject_toml(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""[tool.sql-formatter]\ndialect = \"bigquery\"""")
    config = load_config(str(pyproject))
    assert config["dialect"] == "bigquery"
