import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from statistical_power_analyzer.cli import cli
from click.testing import CliRunner


@pytest.fixture
 def runner():
    return CliRunner()
