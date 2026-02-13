import pytest
import sys
from pathlib import Path

@pytest.fixture(autouse=True)
def add_src(monkeypatch):
    src = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src))
