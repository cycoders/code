from click.testing import CliRunner
from slsa_attestation_verifier.cli import cli

def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
