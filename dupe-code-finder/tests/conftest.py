import pytest
from pathlib import Path


@pytest.fixture
def sample_py(tmp_path: Path):
    a = tmp_path / "a.py"
    a.write_text("def foo(x):\n    return x * 2")
    b = tmp_path / "b.py"
    b.write_text("def double(y):\n    return y * 2")
    return tmp_path


@pytest.fixture
def intra_dupe_py(tmp_path: Path):
    f = tmp_path / "test.py"
    f.write_text("""
def foo(x):
    return x * 2

def bar(z):
    return z * 2
""")
    return tmp_path
