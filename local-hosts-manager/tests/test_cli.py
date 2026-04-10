import typer
test_runner = typer.testing.CliRunner()


def test_cli_list_help(test_runner):
    result = test_runner.invoke(typer.main.get_command(app))
    assert result.exit_code == 0
    assert "Usage" in result.stdout

# Note: Full CLI integration requires mocking HostsManager, covered by unit tests
# Additional e2e via subprocess in CI if needed