import pytest
from pathlib import Path

from type_coverage_cli.analyzer import analyze_directory, find_python_files
from type_coverage_cli.models import OverallStats


@pytest.mark.parametrize("excludes, expected_count", [( ["tests"], 1), ([], 2)])
def test_find_python_files(tmp_path: Path, excludes: list[str], expected_count: int):
    (tmp_path / "a.py").touch()
    (tmp_path / "tests/b.py").touch()
    files = list(find_python_files(tmp_path, excludes))
    assert len(files) == expected_count


def test_analyze_directory(sample_py_file):
    code = """
def foo(a: int, b: str) -> bool:
    pass

def bar(x: int):
    pass

def baz():
    pass
    """
    sample_py_file.write_text(code)
    stats = analyze_directory(sample_py_file.parent, [])
    assert stats.total_funcs == 3  # funcs.total
    assert stats.funcs.typed == 1  # only foo fully typed
    assert stats.funcs.percentage == 33.3
