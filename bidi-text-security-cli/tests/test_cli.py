from click.testing import CliRunner

from bidi_text_security_cli.cli import cli

def test_cli_no_findings(tmp_path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", str(tmp_path)])
    assert result.exit_code == 0
    assert "No bidi" in result.output