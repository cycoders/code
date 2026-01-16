import json
import pytest
from pathlib import Path
from typer.testing import CliRunner

from shell_recorder_cli.cli import app

runner = CliRunner()

@pytest.fixture
def sample_session(tmp_path: Path):
    """Sample .shellrec file."""
    path = tmp_path / "sample.shellrec"
    data = [
        {
            "version": 1,
            "width": 120,
            "height": 24,
            "duration": 1.5,
            "timestamp": 1730000000.0,
            "events_count": 3,
        },
        {"time": 0.1, "stdout": "REC> ls\n"},
        {"time": 0.4, "stdout": "file1.txt  demo/\n"},
        {"time": 1.0, "stdout": "REC> exit\n"},
    ]
    path.write_text(json.dumps(data, indent=2))
    return path
