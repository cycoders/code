import tempfile
from pathlib import Path
from typer.testing import CliRunner

import pytest
from class_diagram_cli.cli import app


runner = CliRunner()


def test_cli_no_classes(tmp_path: Path) -> None:
    result = runner.invoke(app, [str(tmp_path)])
    assert result.exit_code == 1
    assert "No classes found" in result.stdout


def test_cli_success(tmp_path: Path) -> None:
    sample_dir = tmp_path / "samples"
    sample_dir.mkdir()
    (sample_dir / "zoo.py").write_text("class Animal: pass")

    result = runner.invoke(app, [str(sample_dir), "--output", "out.mmd"])
    assert result.exit_code == 0
    assert Path("out.mmd").exists()
    assert "classDiagram" in Path("out.mmd").read_text()


def test_cli_exclude(tmp_path: Path) -> None:
    (tmp_path / "test.py").write_text("class Bad: pass")
    (tmp_path / "good.py").write_text("class Good: pass")

    result = runner.invoke(
        app, [str(tmp_path), "--exclude", "**/test*.py", "--output", "out.mmd"]
    )
    assert result.exit_code == 0
    diagram = Path("out.mmd").read_text()
    assert "Good" in diagram
    assert "Bad" not in diagram


def test_nonexistent_path() -> None:
    result = runner.invoke(app, ["/nonexistent"])
    assert result.exit_code == 1
    assert "Path not found" in result.stdout
