from typer.testing import CliRunner
from log_query_cli.cli import app

runner = CliRunner()


class TestCLI:
    def test_basic_query(self, sample_log):
        result = runner.invoke(app, [
            "SELECT COUNT(*) as total FROM logs",
            str(sample_log)
        ])
        assert result.exit_code == 0
        assert "total" in result.stdout
        assert "4" in result.stdout  # 4 lines parsed

    def test_error_count(self, sample_log):
        result = runner.invoke(app, [
            "SELECT service FROM logs WHERE level = 'ERROR'",
            str(sample_log),
            "--format",
            "table"
        ])
        assert result.exit_code == 0
        assert "db" in result.stdout
        assert "auth" in result.stdout

    def test_chart(self, sample_log):
        result = runner.invoke(app, [
            "SELECT level, COUNT(*) as cnt FROM logs GROUP BY level",
            str(sample_log),
            "--format",
            "chart"
        ])
        assert result.exit_code == 0
        assert "ERROR" in result.stdout
        assert "█" in result.stdout

    def test_nonexistent_file(self):
        result = runner.invoke(app, ["SELECT * FROM logs", "/nonexistent.log"])
        assert result.exit_code == 1
        assert "File not found" in result.stderr

    def test_invalid_sql(self, sample_log):
        result = runner.invoke(app, ["INVALID", str(sample_log)])
        assert result.exit_code == 1
        assert "Query error" in result.stderr