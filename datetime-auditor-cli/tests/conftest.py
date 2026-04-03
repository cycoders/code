import pytest
from pathlib import Path

@pytest.fixture
def test_py_file(tmp_path: Path, source: str):
    """Write source to temp .py file."""
    p = tmp_path / "test.py"
    p.write_text(source)
    return p