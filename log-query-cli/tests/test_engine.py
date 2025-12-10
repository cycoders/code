import polars as pl
from log_query_cli.engine import run_query


class TestEngine:
    @pytest.fixture
    def sample_df(self):
        return pl.DataFrame({
            "level": ["ERROR", "INFO", "ERROR"],
            "service": ["db", "app", "auth"],
            "timestamp": [pl.datetime(2024, 1, 1, 12, 0), pl.datetime(2024, 1, 1, 12, 1), pl.datetime(2024, 1, 1, 12, 2)]
        })

    def test_basic_query(self, sample_df):
        result = run_query(sample_df, "SELECT service, COUNT(*) as cnt FROM logs GROUP BY service")
        assert result["cnt"].to_list() == [1, 1, 1]
        assert sorted(result["service"].to_list()) == ["app", "auth", "db"]

    def test_filter(self, sample_df):
        result = run_query(sample_df, "SELECT * FROM logs WHERE level = 'ERROR'")
        assert len(result) == 2

    def test_time_filter(self, sample_df):
        result = run_query(sample_df, "SELECT COUNT(*) FROM logs WHERE timestamp > '2024-01-01 12:01:00'")
        assert result.item() == 1

    def test_error_handling(self, sample_df):
        # Invalid SQL
        from pytest import raises
        with raises(RuntimeError):
            run_query(sample_df, "INVALID SQL")