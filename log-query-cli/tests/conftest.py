import pytest
import sys
import os
from pathlib import Path
from typer.testing import CliRunner

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from log_query_cli.cli import app

runner = CliRunner()


@pytest.fixture
def sample_log(tmp_path: Path) -> Path:
    log_file = tmp_path / "sample.log"
    log_file.write_text(
        """
{"timestamp": "2024-01-01T12:00:00Z", "level": "INFO", "service": "app", "message": "User logged in"}
{"timestamp": "2024-01-01T12:01:00Z", "level": "ERROR", "service": "db", "message": "Conn failed"}
2024-01-01T12:02:00Z WARN cache: Key miss
[2024-01-01 12:03:00] ERROR auth: Invalid token
        """.strip()
    )
    return log_file