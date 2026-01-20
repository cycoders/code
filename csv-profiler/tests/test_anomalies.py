import pytest
from csv_profiler.anomalies import detect_column_anomalies


def test_high_nulls():
    col_info = {"null_pct": 25.0, "unique_pct": 50.0, "stats": {}}
    anoms = detect_column_anomalies(col_info, 100)
    assert "high_nulls" in " ".join(anoms)


def test_high_cardinality():
    col_info = {"null_pct": 0, "unique_pct": 95.0}
    anoms = detect_column_anomalies(col_info, 100)
    assert "high_cardinality" in " ".join(anoms)


def test_constant():
    col_info = {"unique_pct": 1.0}
    anoms = detect_column_anomalies(col_info, 100)
    assert "constant_value" in " ".join(anoms)