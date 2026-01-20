import pytest
from pathlib import Path
import polars as pl

from csv_profiler.profiler import profile_csv


def test_profile_empty_file(tmp_path: Path):
    p = tmp_path / "empty.csv"
    p.touch()
    result = profile_csv(p, max_rows=10)
    assert result["overview"]["rows"] == 0


def test_profile_sample(sample_csv_path: Path):
    result = profile_csv(sample_csv_path)
    assert result["overview"]["rows"] == 5
    assert result["overview"]["cols"] == 6
    assert "age" in result["columns"]
    age_info = result["columns"]["age"]
    assert age_info["null_pct"] == 20.0
    assert age_info["dtype"].startswith("Int")


def test_max_rows_limits(sample_csv_path: Path):
    result = profile_csv(sample_csv_path, max_rows=2)
    assert result["overview"]["rows"] == 2


def test_anomalies_detect(sample_csv_path: Path):
    result = profile_csv(sample_csv_path)
    anoms = result["anomalies"]["columns"]
    assert any("high_nulls" in str(a) for a in anoms["age"])
    assert result["overview"]["dupe_pct"] > 0