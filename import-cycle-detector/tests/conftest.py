import pytest
from pathlib import Path


@pytest.fixture
def tmp_project(tmp_path: Path):
    """
    Fixture for sample projects.
    """
    return tmp_path