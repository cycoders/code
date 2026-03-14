import json
from typer.testing import CliRunner

from unused_css_finder.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Scan HTML/CSS" in result.stdout


def test_cli_no_args(temp_html_css):
    h, c = temp_html_css
    result = runner.invoke(app, [h, c])
    assert result.exit_code == 0
    assert "%" in result.stdout


def test_cli_json(temp_html_css):
    h, c = temp_html_css
    result = runner.invoke(app, [h, c, "--json"])
    assert result.exit_code == 0
    stats = json.loads(result.stdout)
    assert isinstance(stats, list)
    assert "percent_unused" in stats[0]