def test_cli_help(runner):
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Record" in result.stdout


def test_cli_record_help(runner):
    result = runner.invoke(app, ["record", "--help"])
    assert result.exit_code == 0

@pytest.mark.parametrize("cmd", ["replay", "export", "redact", "delete", "preview"])
def test_cli_commands_help(cmd, runner):
    result = runner.invoke(app, [cmd, "--help"])
    assert result.exit_code == 0


def test_cli_export(sample_session, runner, tmp_path):
    out = str(tmp_path / "out.md")
    result = runner.invoke(app, ["export", str(sample_session), out])
    assert result.exit_code == 0
    assert Path(out).exists()
