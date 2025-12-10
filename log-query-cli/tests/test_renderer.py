import polars as pl
from log_query_cli.renderer import render_df


class TestRenderer:
    def test_table(self, capsys):
        df = pl.DataFrame({"service": ["db", "app"], "cnt": [10, 5]})
        render_df(df, "table")
        captured = capsys.readouterr()
        assert "db" in captured.out
        assert "10" in captured.out

    def test_json(self, capsys):
        df = pl.DataFrame({"a": [1]})
        render_df(df, "json")
        captured = capsys.readouterr()
        assert '{"a":1}' in captured.out

    def test_chart(self, capsys):
        df = pl.DataFrame({"service": ["db", "app"], "cnt": [20, 10]})
        render_df(df, "chart")
        captured = capsys.readouterr()
        assert "db" in captured.out
        assert "█" in captured.out

    def test_empty(self, capsys):
        df = pl.DataFrame({"a": []})
        render_df(df, "table")
        captured = capsys.readouterr()
        assert "0 rows" in captured.out