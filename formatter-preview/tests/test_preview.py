import difflib
import os
import tempfile
from pathlib import Path

import pytest
from unittest.mock import patch, MagicMock

from formatter_preview.preview import (
    get_preview_diff,
    apply_formatter,
    get_formatter,
)


@pytest.fixture
def sample_py_file(tmp_path: Path) -> Path:
    p = tmp_path / "test.py"
    p.write_text('import os,sys\ndef hello():print "hi"')
    return p


@pytest.mark.parametrize(
    "ext,expected",
    [(".py", "ruff"), (".js", "prettier"), (".ts", "prettier"), (".txt", None)],
)
def test_get_formatter(tmp_path: Path, ext: str, expected: str) -> None:
    p = tmp_path / f"test{ext}"
    p.touch()
    assert get_formatter(p) == expected


def test_get_preview_diff_no_change(sample_py_file: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "formatter_preview.preview.subprocess.run",
        lambda *a, **k: MagicMock(returncode=0, stdout=b""),
    )
    p = sample_py_file
    diff = get_preview_diff(p)
    assert diff is None  # Assume no change after mock


@patch("formatter_preview.preview.subprocess.run")
def test_ruff_apply(mock_run: MagicMock, sample_py_file: Path) -> None:
    mock_run.return_value = MagicMock(returncode=0)
    with tempfile.NamedTemporaryFile(suffix=".py") as tmp:
        apply_formatter(tmp.name, "ruff")
        assert mock_run.call_count >= 2  # format + check


def test_non_utf8_skip(tmp_path: Path) -> None:
    p = tmp_path / "binary.bin"
    p.write_bytes(b"\xFF")
    diff = get_preview_diff(p)
    assert diff is None
