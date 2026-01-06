import pytest
from pathlib import Path
from click.testing import CliRunner
from smtp_catcher.cli import app

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def tmp_data_dir(tmp_path: Path):
    dir = tmp_path / "mails"
    dir.mkdir()
    return dir