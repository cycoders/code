import pytest
from context_propagation_auditor.scanner import scan_directory

def test_detects_missing_context(tmp_path):
    code = 'import asyncio\nasyncio.create_task(coro())'
    f = tmp_path / "t.py"
    f.write_text(code)
    assert len(scan_directory(tmp_path)) == 1