import pytest
from curl_history_analyzer.analyzer import compute_stats, _get_group_key
from curl_history_analyzer.parser import parse_history_file
from curl_history_analyzer.models import CurlHistoryEntry

@pytest.fixture
def entries():
    return parse_history_file(Path(__file__).parent / "data" / "sample.jsonl")


def test_group_key():
    assert _get_group_key("https://api.ex.com/foo/bar?x=1", "path") == "/foo/bar"
    assert _get_group_key("https://api.ex.com/", "path") == "/"
    assert _get_group_key("https://api.ex.com", "host") == "api.ex.com"


def test_compute_stats(entries):
    stats = compute_stats(entries, "path")
    assert len(stats) == 2  # /users/octocat, /repos/cycoders/code
    octocat_path = "/users/octocat"
    assert stats[octocat_path].count == 3
    assert stats[octocat_path].error_rate == 0.0
    slow_path = "/data"
    assert "/data" in stats  # from slow.api.example.com/data
    assert stats[slow_path].p95_time == pytest.approx(2.345)
    assert stats[slow_path].error_count == 1


def test_empty(entries):
    empty_stats = compute_stats([], "path")
    assert empty_stats == {}