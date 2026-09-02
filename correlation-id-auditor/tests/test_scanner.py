import tempfile
from pathlib import Path
from correlation_id_auditor.scanner import scan_repository

def test_detects_missing_id_in_requests():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "bad.py"
        p.write_text("import httpx\nhttpx.post('https://example.com')")
        assert any("missing correlation" in i for i in scan_repository(tmp))

def test_ignores_safe_code():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "good.py"
        p.write_text("import httpx\nheaders = {'x-request-id': '123'}\nhttpx.post('https://example.com', headers=headers)")
        assert scan_repository(tmp) == []

def test_handles_async():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "async_bad.py"
        p.write_text("import asyncio\nasync def f(): await asyncio.sleep(0)")
        assert scan_repository(tmp) == []

def test_celery_task():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "celery_bad.py"
        p.write_text("from celery import task\n@task\ndef work(): pass")
        assert any("celery" in i.lower() for i in scan_repository(tmp))

def test_empty_dir():
    with tempfile.TemporaryDirectory() as tmp:
        assert scan_repository(tmp) == []