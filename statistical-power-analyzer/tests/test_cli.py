import click
from click.testing import CliRunner

from statistical_power_analyzer.cli import cli


runner = CliRunner()


def test_analyze_ttest_help():
    result = runner.invoke(cli, ["analyze", "--help"])
    assert result.exit_code == 0


def test_analyze_sample_size():
    result = runner.invoke(
        cli,
        "analyze --test-type ttest-ind --effect-size 0.5 --power 0.8 --solve-for nobs".split(),
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "nobs1" in result.stdout
    assert "63" in result.stdout


def test_plot_requires_output():
    result = runner.invoke(cli, ["plot", "--test-type", "ttest-ind", "--effect-size", "0.5"])
    assert result.exit_code != 0
    assert "--output" in result.stdout


def test_invalid_alpha():
    result = runner.invoke(
        cli, "analyze --test-type ttest-ind --effect-size 0.5 --alpha -0.1".split()
    )
    assert result.exit_code != 0
    assert "Error" in result.stderr
