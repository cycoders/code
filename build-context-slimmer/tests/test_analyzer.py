import pytest
from pathlib import Path
from build_context_slimmer.analyzer import get_all_file_sizes, get_used_files


@pytest.fixture
def sample_context(tmp_path: Path) -> Path:
    ctx = tmp_path / "ctx"
    ctx.mkdir()

    (ctx / "src" / "a.py").write_text("a")
    (ctx / "src" / "sub" / "b.txt").write_text("b")
    (ctx / "other.md").write_text("o")
    (ctx / "static" / "img.png").touch()

    return ctx


def test_all_sizes(sample_context: Path) -> None:
    sizes = get_all_file_sizes(sample_context)
    assert len(sizes) == 4
    assert sample_context / "src" / "a.py" in sizes


def test_dir_copy(sample_context: Path) -> None:
    used = get_used_files(sample_context, ["src/"])
    assert len(used) == 2
    assert sample_context / "src" / "a.py" in used
    assert sample_context / "other.md" not in used


def test_file_glob(sample_context: Path) -> None:
    (sample_context / "app.py").write_text("py")
    used = get_used_files(sample_context, ["*.py"])
    assert len(used) == 2  # a.py + app.py
    assert sample_context / "other.md" not in used


def test_matched_dir(sample_context: Path) -> None:
    (sample_context / "mydir" / "file.txt").write_text("f")
    used = get_used_files(sample_context, ["mydir"])
    assert sample_context / "mydir" / "file.txt" in used


def test_empty_patterns(sample_context: Path) -> None:
    used = get_used_files(sample_context, [])
    assert used == set()


def test_nonexistent_dir(sample_context: Path) -> None:
    used = get_used_files(sample_context, ["missing/"])
    assert used == set()
