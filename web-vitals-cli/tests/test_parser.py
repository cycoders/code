import pytest
from web_vitals_cli.parser import parse_lighthouse_json
from web_vitals_cli.types import Metric


def test_parse_lighthouse_json(sample_lh_json, sample_result):
    assert sample_result.overall_score == 0.92
    assert "lcp" in sample_result.metrics
    lcp = sample_result.metrics["lcp"]
    assert lcp.displayValue == "1.8 s"
    assert lcp.numericValue == 1800.0


def test_missing_audit(sample_lh_json):
    data = sample_lh_json.copy()
    data["audits"].pop("largest-contentful-paint")
    result = parse_lighthouse_json(data)
    assert result.metrics["lcp"].displayValue == "N/A"
    assert result.metrics["lcp"].numericValue == 0.0