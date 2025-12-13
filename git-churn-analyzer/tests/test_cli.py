import pytest
from typer.testing import CliRunner

from git_churn_analyzer.cli import app

runner = CliRunner()


def test_version(mocker):
    mocker.patch("sys.argv", ["prog", "version"])
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


@pytest.mark.parametrize(
    "args, expect_fail",
    [
        (["analyze"], False),
        (["analyze", "--format=invalid"], True),
        (["analyze", "--repo=/nonexistent"], True),
    ],
)
def test_analyze(mocker, mock_git_log, args, expect_fail):
    mock_git_log.return_value.decode.return_value = "sample output"
    mocker.patch("git_churn_analyzer.cli.parse_git_log", return_value=[])
    mocker.patch("git_churn_analyzer.cli.analyze_commits", return_value={})
    result = runner.invoke(app, ["analyze"] + args)
    assert result.exit_code == (1 if expect_fail else 0)


def test_bad_repo(mocker, mock_git_log):
    mocker.patch("subprocess.check_output", side_effect=FileNotFoundError)
    result = runner.invoke(app, ["analyze"])
    assert result.exit_code == 1
    assert "'git' command not found" in result.stderr
