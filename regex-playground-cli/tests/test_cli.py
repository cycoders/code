import pytest

from regex_playground_cli.cli import app


@pytest.mark.parametrize(
    "cmd_args, expected",
    [
        (["explain", r"\\d+"], "digit"),
        (["explain", "/^foo$/m"], "multiline"),
        (["explain", "/[a-z]/"], "character class"),
    ],
)
def test_explain(runner, cmd_args, expected):
    result = runner.invoke(app, cmd_args)
    assert result.exit_code == 0
    assert expected in result.stdout


def test_explain_invalid(runner):
    result = runner.invoke(app, ["explain", "["])
    assert result.exit_code == 1
    assert "Invalid regex" in result.stderr


def test_test_batch(runner, tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text("error line1\nnoerror\nERROR line3")
    result = runner.invoke(
        app, ["test", "/error/i", "--file", str(log_file)]
    )
    assert result.exit_code == 0
    outputs = result.stdout.strip().split("\n")
    assert len(outputs) == 2  # 2 matching lines
    import json
    data1 = json.loads(outputs[0])
    assert data1["num_matches"] == 1
