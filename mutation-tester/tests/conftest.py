import pytest
from pathlib import Path


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """Sample project with code + tests."""
    proj = tmp_path / "sample_proj"
    proj.mkdir()

    # foo.py with mutations
    (proj / "foo.py").write_text("""
def add(a, b):
    return a + b

def mul(a, b):
    return a * b
""")

    # bar.py with if
    (proj / "bar.py").write_text("""
def safe(x):
    if x > 0:
        return True
    return False
""")

    # tests
    tests_dir = proj / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_foo.py").write_text("""
from foo import add, mul


def test_add():
    assert add(1, 2) == 3


def test_mul():
    assert mul(2, 3) == 6
""")
    (tests_dir / "test_bar.py").write_text("""
from bar import safe


def test_safe():
    assert safe(5)
    assert not safe(-1)
""")

    return proj