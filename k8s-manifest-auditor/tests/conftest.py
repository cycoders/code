import pytest
from pathlib import Path


@pytest.fixture
def examples_dir() -> Path:
    return Path(__file__).parent.parent / "examples"