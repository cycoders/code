import pytest
from log_anomaly_detector.anomaly import find_anomalies
from log_anomaly_detector.config import AnomalyConfig
from .conftest import sample_df


def test_empty_df():
    df = find_anomalies(pd.DataFrame(), AnomalyConfig(fields=["x"]))
    assert df.empty


def test_basic_detection(sample_df):
    cfg = AnomalyConfig(fields=["duration_ms"])
    anoms = find_anomalies(sample_df, cfg)
    assert len(anoms) == 1
    assert anoms["is_anomaly"].all()


def test_groupby_detection(sample_df):
    cfg = AnomalyConfig(fields=["duration_ms"], group_by=["user_id"])
    anoms = find_anomalies(sample_df, cfg)
    assert len(anoms) == 1  # outlier in u1 group


def test_missing_field(sample_df):
    cfg = AnomalyConfig(fields=["missing"])
    anoms = find_anomalies(sample_df, cfg)
    assert anoms.empty
