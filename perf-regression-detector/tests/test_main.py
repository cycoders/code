import os
from perf_regression_detector.main import cli
from tests.conftest import runner


def test_cli_init(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli, ["init"])
    assert result.exit_code == 0
    assert (tmp_path / "perf-regression.yaml").exists()


def test_cli_help():
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0