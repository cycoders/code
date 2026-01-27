import pytest
from typer.testing import Result
from formatter_preview.cli import app


@pytest.mark.parametrize("command", ["preview", "check", "apply"])
def test_help(cli_runner: pytest.PostponedFixture) -> None:
    result: Result = cli_runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_preview_no_args(cli_runner, mock_subprocess) -> None:
    result = cli_runner.invoke(app, ["preview"])
    assert result.exit_code == 0  # No files -> green exit 0
