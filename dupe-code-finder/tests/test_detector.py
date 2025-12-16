import pytest
from pathlib import Path

from dupe_code_finder.detector import detect_dupes, CodeBlock
from dupe_code_finder.tokenizer import tokenize_source


class TestDetector:
    def test_detects_inter_file_dupes(self, sample_py):
        dupes = detect_dupes(sample_py, min_tokens=5, threshold=0.8)
        assert len(dupes) >= 1
        sim, b1, b2 = dupes[0]
        assert sim > 0.9
        assert b1.path.endswith("a.py")
        assert b2.path.endswith("b.py")

    def test_detects_intra_file_dupes(self, intra_dupe_py):
        dupes = detect_dupes(intra_dupe_py, min_tokens=5, threshold=0.8)
        assert len(dupes) >= 1
        sim, b1, b2 = dupes[0]
        assert sim > 0.95
        assert b1.path == b2.path

    def test_no_dupes_empty(self, tmp_path):
        dupes = detect_dupes(tmp_path, threshold=0.99)
        assert len(dupes) == 0

    def test_ignores_dirs(self, tmp_path):
        (tmp_path / "venv" / "a.py").write_text("code")
        (tmp_path / ".git" / "b.py").write_text("code")
        dupes = detect_dupes(tmp_path)
        assert len(dupes) == 0  # ignored

    def test_small_blocks_skipped(self, sample_py):
        dupes = detect_dupes(sample_py, min_tokens=100, threshold=0.8)
        assert len(dupes) == 0
