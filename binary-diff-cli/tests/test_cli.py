import os
from typer.testing import CliRunner

from binary_diff_cli.cli import app

runner = CliRunner()


def test_diff_smoke(tmp_bins):
    f1, f2, _, _ = tmp_bins
    result = runner.invoke(app, ["diff", str(f1), str(f2)])
    assert result.exit_code == 0
    assert "08x" in result.stdout  # offset format
    assert "#Chg" in result.stdout


def test_analyze_smoke(tmp_bins):
    f1, f2, _, _ = tmp_bins
    result = runner.invoke(app, ["analyze", str(f1), str(f2)])
    assert result.exit_code == 0
    assert "Size" in result.stdout
    assert "Entropy" in result.stdout


def test_plot_smoke(tmp_bins):
    f1, _, _, _ = tmp_bins
    result = runner.invoke(app, ["plot", str(f1), "--type", "entropy"])
    assert result.exit_code == 0
    assert "█" in result.stdout or "░" in result.stdout


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "diff" in result.stdout
    assert "analyze" in result.stdout


def test_bad_file():
    result = runner.invoke(app, ["diff", "/nope", "/nope"])
    assert result.exit_code != 0
    assert "Error" in result.stderr
