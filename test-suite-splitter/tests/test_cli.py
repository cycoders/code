import json
from pathlib import Path
from typer.testing import CliRunner

import pytest
from test_suite_splitter.cli import app


@pytest.fixture
 def runner() -> CliRunner:
    return CliRunner()


class TestCLI:
    def test_split_sample_table(self, sample_xml: Path, runner: CliRunner) -> None:
        result = runner.invoke(app, ["split", str(sample_xml), "--jobs", "2", "--output", "table"])
        assert result.exit_code == 0
        assert "Loaded 5 tests" in result.stdout
        assert "Balance: " in result.stdout
        assert "pytest -k" in result.stdout

    def test_split_json(self, sample_xml: Path, runner: CliRunner) -> None:
        result = runner.invoke(app, ["split", str(sample_xml), "--jobs", "2", "--output", "json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["meta"]["total_tests"] == 5
        assert len(data["jobs"]) == 2

    def test_no_args_error(self, runner: CliRunner) -> None:
        result = runner.invoke(app)
        assert result.exit_code != 0
        assert "Usage:" in result.stdout

    def test_invalid_jobs(self, sample_xml: Path, runner: CliRunner) -> None:
        result = runner.invoke(app, ["split", str(sample_xml), "--jobs", "0"])
        assert result.exit_code != 0
        assert "num_jobs must be >= 1" in result.stderr

    def test_version(self, runner: CliRunner) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout

    def test_no_tests_error(self, empty_xml: Path, runner: CliRunner) -> None:
        result = runner.invoke(app, ["split", str(empty_xml)])
        assert result.exit_code == 1
        assert "No tests found" in result.stdout