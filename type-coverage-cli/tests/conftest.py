import pytest
from pathlib import Path

@pytest.fixture
def sample_py_file(tmp_path: Path, code: str):
    """Write code to temp py file."""
    p = tmp_path / "test.py"
    p.write_text(code)
    return p