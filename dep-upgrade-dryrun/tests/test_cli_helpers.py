import pytest
from pathlib import Path
from upgrade_dryrun.cli import find_workspaces
from upgrade_dryrun.ecosystems import ecosystems


def test_find_workspaces(tmp_path: Path):
    # NPM workspace
    npm_dir = tmp_path / "npm-proj"
    npm_dir.mkdir()
    (npm_dir / "package.json").touch()
    (npm_dir / "package-lock.json").touch()

    # Poetry workspace
    poetry_dir = tmp_path / "poetry-proj"
    poetry_dir.mkdir()
    (poetry_dir / "pyproject.toml").touch()
    (poetry_dir / "poetry.lock").touch()

    # Nested
    nested = tmp_path / "deep" / "cargo-proj"
    nested.mkdir(parents=True)
    (nested / "Cargo.toml").touch()
    (nested / "Cargo.lock").touch()

    ecos = [ecosystems["npm"], ecosystems["poetry"], ecosystems["cargo"]]
    ws = list(find_workspaces(tmp_path, ecos))

    assert len(ws) == 3
    assert any(eco.name == "npm" and ws_path == npm_dir for eco, ws_path in ws)
    assert any(eco.name == "poetry" and ws_path == poetry_dir for eco, ws_path in ws)
    assert any(eco.name == "cargo" and ws_path == nested for eco, ws_path in ws)
