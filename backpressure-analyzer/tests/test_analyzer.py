import tempfile
from pathlib import Path
from backpressure_analyzer.analyzer import analyze_path

def test_detects_queue():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "t.py"
        p.write_text("import asyncio\nq = asyncio.Queue()\n")
        assert len(analyze_path(tmp)) == 1

def test_ignores_sync_code():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "t.py"
        p.write_text("q = list()\n")
        assert len(analyze_path(tmp)) == 0

def test_multiple_findings():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "t.py"
        p.write_text("import asyncio\nq = asyncio.Queue()\nasyncio.create_task(x)\n")
        assert len(analyze_path(tmp)) == 2
