import json
import pytest
from pathlib import Path
from typer.testing import CliRunner

from websocket_tester.cli import app

runner = CliRunner()

@pytest.fixture
def sample_session(tmp_path: Path):
    p = tmp_path / "demo.jsonl"
    p.write_text(
        '{"ts":"2024-...","direction":"out","payload":{"ping":true}}\n'
        '{"ts":"2024-...","direction":"in","payload":{"pong":true}}\n'
    )
    return p

@pytest.fixture
def mock_client(monkeypatch):
    # Simplified for unit
    class MockWS:
        def __init__(self):
            self.closed = False
        async def send(self, msg):
            pass
        async def recv(self):
            return None
        async def close(self):
            pass
    monkeypatch.setattr("websocket_tester.websocket_client.WSClient", MockWS)
