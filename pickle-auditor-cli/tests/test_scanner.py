import tempfile
from pathlib import Path
from pickle_auditor_cli.scanner import scan_directory

def test_detects_pickle():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "bad.py"
        p.write_text("import pickle\npickle.load(open('x'))")
        assert len(scan_directory(tmp)) == 1

def test_ignores_safe_yaml():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "good.py"
        p.write_text("import yaml\nyaml.safe_load(open('x'))")
        assert len(scan_directory(tmp)) == 0