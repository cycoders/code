import json
import pytest
from typer.testing import CliRunner

from serdes_bench.cli import app

runner = CliRunner()


@pytest.fixture
def sample_data():
    return {
        "key": "value",
        "num": 42,
        "list": [1, 2, 3],
        "nested": {"a": {"b": True}},
    }


@pytest.fixture
def sample_bytes():
    return b'{"key":"value"}'
