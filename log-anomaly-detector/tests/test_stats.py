import pytest
import numpy as np
import pandas as pd

from log_anomaly_detector.stats import detect_outliers


@pytest.fixture
def normal_series():
    return pd.Series([1, 2, 3, 4, 5])


@pytest.fixture
def outlier_series():
    return pd.Series([1, 2, 3, 4, 100])


@pytest.mark.parametrize("method", ["zscore", "iqr", "modified_z"])
def test_no_outliers_normal(normal_series, method):
    mask = detect_outliers(normal_series, method)
    assert not mask.any()


@pytest.mark.parametrize("method", ["zscore", "iqr", "modified_z"])
def test_detect_outlier(outlier_series, method):
    mask = detect_outliers(outlier_series, method)
    assert mask.iloc[-1] is True
    assert mask.sum() >= 1


def test_short_series():
    s = pd.Series([1, 2])
    mask = detect_outliers(s)
    assert not mask.any()


def test_all_equal():
    s = pd.Series([42] * 10)
    mask = detect_outliers(s, method="modified_z")
    assert not mask.any()
