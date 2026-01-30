import pytest
from pathlib import Path

@pytest.fixture
def sample_jsonl(tmp_path: Path):
    content = '''
{{"timestamp": "2024-01-01T10:00:00Z", "trace_id": "t1", "span_id": "s1", "service": "frontend", "name": "handle", "duration_ms": 100}}
{{"timestamp": "2024-01-01T10:00:01Z", "trace_id": "t1", "span_id": "s2", "parent_span_id": "s1", "service": "backend", "name": "process", "duration_ms": 50}}
{{"timestamp": "2024-01-01T10:00:00.5Z", "trace_id": "t2", "span_id": "s3", "service": "frontend", "name": "other", "duration_ms": 20}}
'''
    p = tmp_path / "sample.jsonl"
    p.write_text(content)
    return p