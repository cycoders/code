import typer
from pathlib import Path
from click.testing import CliRunner
from critical_css_extractor.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Extract critical CSS" in result.stdout


def test_cli_extract(tmp_path: Path, sample_html, sample_css):
    html_p = tmp_path / "index.html"
    html_p.write_text(sample_html)
    css_p = tmp_path / "styles.css"
    css_p.write_text(sample_css)
    result = runner.invoke(app, [str(html_p), "--css", str(css_p), "--output", "out.css"])
    assert result.exit_code == 0
    assert Path("out.css").exists()