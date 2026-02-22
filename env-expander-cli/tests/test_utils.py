import pytest
from pathlib import Path
from env_expander_cli.utils import load_env, dump_env


def test_load_env(tmp_path: Path):
    env_path = tmp_path / ".env"
    env_path.write_text('A=1\nB="2 3"\nC=\'quoted\'')
    env = load_env(env_path)
    assert env == {"A": "1", "B": "2 3", "C": "quoted"}


def test_load_env_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_env(tmp_path / "missing.env")


def test_dump_env(tmp_path: Path):
    out = tmp_path / "out.env"
    dump_env({"A": "hello world", "B": ""}, out)
    content = out.read_text()
    assert "A='hello world'" in content
    assert "B=" in content


def test_dump_json(tmp_path: Path):
    out = tmp_path / "out.json"
    dump_env({"A": "1"}, out, json_output=True)
    assert out.read_text().startswith("{\"A\": \"1\"}")