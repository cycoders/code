import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def cleanup(tmp_path: Path):
    yield
    # Ensure cleanup after