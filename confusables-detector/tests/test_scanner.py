import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from rich.console import Console

from confusables_detector.scanner import (
    find_text_files,
    process_file,
    scan_directory,
)


@pytest.fixture
def temp_dir(tmp_path: Path):
    d = tmp_path / "testrepo"
    d.mkdir()
    (d / "good.py").write_text("def main(): pass")
    (d / "bad.py").write_text("def mаin(): pass")  # Cyrillic a
    (d / "binary.png").write_text("fake")
    (d / ".git" / "config").mkdir(parents=True).write_text("ignore")
    (d / "node_modules" / "x.js").mkdir(parents=True).write_text("ignore")
    return d


def test_find_text_files(temp_dir: Path):
    files = list(find_text_files(temp_dir))
    assert len(files) == 2  # good.py, bad.py
    assert Path(temp_dir, "good.py") in files
    assert Path(temp_dir, "binary.png") not in files
    assert Path(temp_dir, ".git") not in files


@pytest.mark.parametrize("excludes", [[], ["*.png"]])
def test_find_text_files_excludes(temp_dir: Path, excludes):
    files = list(find_text_files(temp_dir, excludes))
    assert len(files) == 2


def test_process_file():
    fp = Path("test.py")
    fp.write_text("hello ｗorld")
    issues = []
    stats = {"files": 0, "lines": 0, "confusables": 0}
    process_file(fp, issues, stats)
    assert stats["confusables"] == 1
    assert len(issues) == 1
    assert issues[0]["count"] == 1


@patch("confusables_detector.scanner.find_text_files")
@patch("confusables_detector.scanner.process_file")
def test_scan_directory(mock_process, mock_find, temp_dir: Path):
    mock_find.return_value = [Path("test.py")]
    mock_process.side_effect = lambda fp, issues, stats: stats.update(
        {"lines": 10, "confusables": 2}
    )
    console = Console(record=True)
    stats = scan_directory(console, temp_dir, [], False)
    assert stats["confusables"] == 2
    assert stats["files"] == 1
