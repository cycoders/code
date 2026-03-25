import pytest
from pathlib import Path
from pem_tool_cli.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_split(tmp_path, sample_cert_pem, sample_key_pem):
    mixed = tmp_path / "mixed.pem"
    mixed.write_text(sample_cert_pem + "\n" + sample_key_pem)
    result = runner.invoke(app, ["split", str(mixed)])
    assert result.exit_code == 0
    assert len(list(tmp_path.glob("mixed.*.pem"))) == 2