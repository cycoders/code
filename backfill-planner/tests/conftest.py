import pytest
from pathlib import Path
from typer.testing import CliRunner

from backfill_planner.cli import app


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_config_dict():
    return {
        "table": "users",
        "total_rows": 1000000,
        "write_throughput_avg": 1000.0,
        "row_size_bytes": 1024,
        "strategy": "online-batched",
        "dialect": "postgresql",
    }
