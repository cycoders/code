import json
import pytest
from pathlib import Path

from h2_priority_analyzer.parser import parse_netlog


@pytest.fixture
def sample_netlog_path() -> Path:
    path = Path(__file__).parent / "data" / "sample-netlog.jsonl"
    path.parent.mkdir(exist_ok=True)
    # Create sample if not exists
    if not path.exists():
        path.write_text('{"sourceType":"HTTP2_STREAM","source":{"id":1},"type":"HTTP2_STREAM_RECV_PRIORITY","time":1000000,"params":{"dependency":0,"weight":201}}')
    return path
