import typer
from click.testing import CliRunner
from k8s_manifest_auditor.main import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Audit Kubernetes manifests" in result.stdout

# Note: Full CLI tests require patching paths/stdout
