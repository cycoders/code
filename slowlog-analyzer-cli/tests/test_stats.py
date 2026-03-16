import pytest
from slowlog_analyzer_cli.stats import compute_stats
from slowlog_analyzer_cli.models import SlowQuery


@pytest.fixture
def sample_queries():
    return [
        SlowQuery("ts", 100.0, "u", "d", "select * from users where id=?"),
        SlowQuery("ts", 200.0, "u", "d", "select * from users where id=?"),
        SlowQuery("ts", 150.0, "u", "d", "select * from posts"),
    ]


def test_compute_stats(sample_queries):
    df, samples = compute_stats(sample_queries, top_n=10)
    assert len(df) == 2
    assert df["count"][0] == 2
    assert df["avg_duration_ms"][0] == 150.0
    assert len(samples) == 2
