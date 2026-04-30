import shutil
import sys
from pathlib import Path

pytest_plugins = []


@pytest.fixture(autouse=True)
def setup_venv(monkeypatch: pytest.MonkeyPatch):
    # Mock venv for tests
    pass


@pytest.fixture
def datadir(tmp_path: Path):
    return tmp_path