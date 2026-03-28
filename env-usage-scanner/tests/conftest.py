import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir() -> Path:
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)
