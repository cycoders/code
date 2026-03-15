import pytest
from log_anomaly_detector.parser import parse_batch, parse_line


@pytest.mark.parametrize(
    "line,expected",
    [
        ('{"a":1}', {"a": 1}),
        ("{\"duration\":500}", {"duration": 500}),
        ("bad json", None),
        ("", None),
        ("   ", None),
    ],
)
def test_parse_line(line, expected):
    assert parse_line(line) == expected


def test_parse_batch(sample_jsonl, tmp_path):
    df = parse_batch(str(sample_jsonl))
    assert len(df) == 2
    assert "duration_ms" in df.columns
    assert df["duration_ms"].dtype == "int64"


def test_parse_batch_stdin(capfd):
    sys.stdin = open("nonexistent")  # mock
    pytest.skip("Stdin tested via CLI")
