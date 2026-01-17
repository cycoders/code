import json
from pathlib import Path
import pytest
from jsonl_processor.processor import (
    stream_dicts,
    run_filter,
    run_transform,
    run_sample,
    run_aggregate,
    run_stats,
    output_writer,
)


def test_stream_dicts(sample_jsonl: Path):
    data_lines = list(stream_dicts(str(sample_jsonl), strict=False))
    assert len(data_lines) == 5  # skips malformed
    assert data_lines[0][0]["id"] == 1


def test_stream_dicts_strict_raises(sample_jsonl: Path):
    list(stream_dicts(str(sample_jsonl), strict=True))  # no raise, has malformed
    with pytest.raises(ValueError):
        list(stream_dicts(str(sample_jsonl.replace("sample.jsonl", "malformed.jsonl")), strict=True))


def test_filter(tmp_path: Path, sample_jsonl: Path):
    out = tmp_path / "filtered.jsonl"
    run_filter(str(sample_jsonl), str(out), "age", ">", 18, strict=False, verbose=False)
    lines = out.read_text().splitlines()
    assert len(lines) == 3
    ages = [json.loads(l)["age"] for l in lines]
    assert all(a > 18 for a in ages)


def test_transform(tmp_path: Path, sample_jsonl: Path):
    out = tmp_path / "transformed.jsonl"
    run_transform(str(sample_jsonl), str(out), "region", strict=False, verbose=False)
    lines = out.read_text().splitlines()
    assert len(lines) == 5
    regions = [json.loads(l) for l in lines]
    assert all(isinstance(r, str) for r in regions)


def test_sample(tmp_path: Path, sample_jsonl: Path):
    out = tmp_path / "sampled.jsonl"
    run_sample(str(sample_jsonl), str(out), 0.4, strict=False, verbose=False)
    lines = out.read_text().splitlines()
    assert 1 <= len(lines) <= 5  # probabilistic


def test_aggregate(tmp_path: Path, sample_jsonl: Path):
    out = tmp_path / "agg.jsonl"
    run_aggregate(str(sample_jsonl), str(out), "region", "sum:revenue,avg:age,count", strict=False, verbose=False)
    lines = out.read_text().splitlines()
    assert len(lines) == 3  # US EU ASIA
    us = json.loads([l for l in lines if 'US' in l][0])
    assert us["count"] == 2
    assert us["sum_revenue"] == 220.0
    assert abs(us["avg_age"] - 27.5) < 0.1


def test_stats(sample_jsonl: Path, capsys):
    run_stats(str(sample_jsonl), "count,unique:region,sum:revenue", strict=False, verbose=False)
    captured = capsys.readouterr()
    assert "Count" in captured.out
    assert "Unique region" in captured.out
    assert "5" in captured.out  # count
    assert "3" in captured.out  # unique region