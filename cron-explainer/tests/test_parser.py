import pytest
from cron_explainer.parser import explain, next_runs

def test_explain_simple():
    assert "At" in explain("0 9 * * 1-5")

def test_explain_at():
    assert explain("@daily") == "daily"

def test_next_runs_count():
    runs = next_runs("0 0 * * *", "UTC", 3)
    assert len(runs) == 3

def test_invalid_field_count():
    with pytest.raises(ValueError):
        explain("* * * *")

def test_timezone_respected():
    runs = next_runs("0 0 * * *", "Europe/London", 1)
    assert runs[0].tzinfo is not None