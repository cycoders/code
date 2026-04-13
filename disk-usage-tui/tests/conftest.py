import pytest
import tempfile
import shutil
from pathlib import Path

@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)