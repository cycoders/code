import os
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

runner = CliRunner()

@pytest.fixture(autouse=True)
def chdir():
    os.chdir(Path(__file__).parent)