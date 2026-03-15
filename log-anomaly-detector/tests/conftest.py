import pytest
import pandas as pd
import sys

from pathlib import Path


@pytest.fixture(autouse=True)
def setup_venv(monkeypatch):
    """Mock venv activation."""
    monkeypatch.syspath_prepend("src")


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "duration_ms": [10, 20, 30, 40, 5000, 15, 25],
        "user_id": ["u1", "u1", "u2", "u2", "u1", "u2", "u1"],
        "level": ["INFO"] * 7,
    })


@pytest.fixture
def sample_jsonl(tmp_path: Path):
    p = tmp_path / "test.jsonl"
    p.write_text(
        '{"duration_ms":10,"user_id":"u1","level":"INFO"}\n'
        '{"duration_ms":5000,"user_id":"u1","level":"INFO"}\n'
    )
    return p
