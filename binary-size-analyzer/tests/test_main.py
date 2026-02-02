import typer
from typer.testing import CliRunner
from unittest.mock import patch, ANY

from binary_size_analyzer.main import app
from binary_size_analyzer.analyzer import analyze_binary


runner = CliRunner()


class TestCLI:
    def test_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Inspect binary size breakdown" in result.stdout

    @patch("binary_size_analyzer.analyzer.analyze_binary")
    def test_inspect_valid(self, mock_analyze):
        mock_data = {"overall": {"format": "ELF"}}
        mock_analyze.return_value = mock_data

        result = runner.invoke(app, ["inspect", "test.bin"])
        assert result.exit_code == 0
        mock_analyze.assert_called_once_with("test.bin")

    @patch("binary_size_analyzer.analyzer.analyze_binary")
    def test_inspect_json(self, mock_analyze):
        mock_analyze.return_value = {"key": "value"}
        result = runner.invoke(app, ["inspect", "test.bin", "--format", "json"])
        assert result.exit_code == 0
        assert '{"key": "value"}' in result.stdout

    def test_file_not_found(self):
        result = runner.invoke(app, ["inspect", "/nonexistent"])
        assert result.exit_code == 1
        assert "not found" in result.stderr