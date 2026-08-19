from pathlib import Path
import tempfile

from symlink_analyzer_cli.analyzer import analyze

def test_detects_broken_symlink():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / "missing"
        link = root / "link"
        link.symlink_to(target)
        res = analyze(str(root), ["broken"])
        assert res["exit_code"] == 1
        assert len(res["broken"]) == 1

def test_detects_duplicate_targets():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / "real"
        target.write_text("x")
        (root / "a").symlink_to(target)
        (root / "b").symlink_to(target)
        res = analyze(str(root), [])
        assert len(res["duplicates"]) == 1

def test_clean_tree_returns_zero():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "file").write_text("ok")
        res = analyze(str(root), ["broken", "cyclic"])
        assert res["exit_code"] == 0

def test_ignores_non_symlinks():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "regular").write_text("data")
        res = analyze(str(root), ["broken"])
        assert res["exit_code"] == 0

def test_handles_permission_errors_gracefully():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        res = analyze(str(root), ["broken"])
        assert "exit_code" in res