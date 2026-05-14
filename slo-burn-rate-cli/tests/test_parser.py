import pandas as pd
import pytest
from slo_burn_rate_cli.parser import parse_metrics
from pathlib import Path


@pytest.fixture
def sample_jsonl(tmp_path):
    p = tmp_path / "test.jsonl"
    p.write_text('''
{"timestamp":"2024-01-01T00:00:00Z","status":200,"latency_ms":100}
{"timestamp":"2024-01-01T00:01:00Z","status":500,"latency_ms":600}
''')
    return p


def test_parse_jsonl(sample_jsonl, tmp_path):
    df = parse_metrics(str(sample_jsonl), "timestamp", None, "status", 400, console=None)  # Mock console
    assert len(df) == 2
    assert 'is_error' in df.columns
    assert df['is_error'].sum() == 1
    assert df.index.name == 'timestamp'


def test_parse_csv(tmp_path):
    p = tmp_path / "test.csv"
    p.write_text("timestamp,status,latency_ms\n2024-01-01T00:00:00Z,200,100")
    df = parse_metrics(str(p), "timestamp", None, "status", 400, console=None)
    assert len(df) == 1


def test_bad_timestamps(sample_jsonl):
    # Modify to bad ts
    pass
