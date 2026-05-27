from typer.testing import CliRunner
from ulid_toolkit.cli import app

runner = CliRunner()

def test_generate_command():
    result = runner.invoke(app, ["generate", "--count", "3"])
    assert result.exit_code == 0
    assert len(result.stdout.splitlines()) == 3