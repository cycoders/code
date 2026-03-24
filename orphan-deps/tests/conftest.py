import pathlib
from typing import Iterator

import pytest
from typer.testing import CliRunner

from orphan_deps.cli import app

@pytest.fixture
 def runner() -> CliRunner:
    return CliRunner()

@pytest.fixture
 def sample_project(tmp_path: pathlib.Path) -> Iterator[pathlib.Path]:
    """Sample project dir."""
    proj = tmp_path / "proj"
    proj.mkdir()

    (proj / "src").mkdir()
    (proj / "src / foo.py").write_text('import requests\nfrom flask import Flask')
    (proj / "tests / test_bar.py").write_text('import pytest\nimport numpy')

    reqs = proj / "requirements.txt"
    reqs.write_text("requests==2.28.0\nflask\nunused-pkg==1.0\nnumpy\n")

    pyproj = proj / "pyproject.toml"
    pyproj.write_text("[tool.poetry.dependencies]\npython = '^3.11'\nrequests = '*'\nunused2 = '*'[project.dependencies]\nflask = '*'\n")

    yield proj

    # Cleanup not needed