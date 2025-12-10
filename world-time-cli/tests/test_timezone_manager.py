import pytest
from datetime import datetime, timezone

from src.timezone_manager import (
    DEFAULT_TZS,
    get_current_time,
    search_timezones,
)


def test_get_current_time_ny():
    utc_now = datetime(2024, 10, 15, 12, 0, 0, tzinfo=timezone.utc)
    result = get_current_time("America/New_York", utc_now)
    assert result["name"] == "America/New_York"
    assert result["offset"] == "UTC-4"
    assert result["time"] == "08:00"
    assert result["date"].startswith("2024-10-15")


def test_get_current_time_london():
    utc_now = datetime(2024, 10, 15, 12, 0, 0, tzinfo=timezone.utc)
    result = get_current_time("Europe/London", utc_now)
    assert result["name"] == "Europe/London"
    assert result["offset"] == "UTC+1"
    assert result["time"] == "13:00"
    assert result["date"].startswith("2024-10-15")


def test_search_timezones_berlin():
    results = search_timezones("Berlin")
    assert "Europe/Berlin" in results


def test_search_timezones_no_match():
    results = search_timezones("xyzzy123nonexistent")
    assert len(results) == 0


def test_invalid_timezone():
    utc_now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="Invalid timezone"):
        get_current_time("Invalid/TZ", utc_now)


def test_default_tzs():
    assert len(DEFAULT_TZS) == 6
    assert "America/New_York" in DEFAULT_TZS