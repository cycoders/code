import pytest
from click.testing import CliRunner
from pathlib import Path

from build_context_slimmer.cli import app


runner = CliRunner()


def test_scan_help() -> None:
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0


@pytest.mark.parametrize("missing", [True, False])
def test_scan_dockerfile(tmp_path: Path, missing: bool) -> None:
    if not missing:
        (tmp_path / "Dockerfile").touch()

    result = runner.invoke(app, ["scan"], cwd=tmp_path)
    if missing:
        assert result.exit_code == 1
        assert "not found" in result.stdout
    else:
        assert result.exit_code == 0
