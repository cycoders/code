import pytest
from pathlib import Path


@pytest.fixture
def poetry_pyproject(tmp_path: Path) -> Path:
    p = tmp_path / "pyproject.toml"
    p.write_text('''
[tool.poetry.dependencies]
python = "^3.11"
requests = "^2.31.0"
pydantic = {version = ">=2.0", extras = ["email"]}
''')
    return p


@pytest.fixture
def pep621_pyproject(tmp_path: Path) -> Path:
    p = tmp_path / "pyproject.toml"
    p.write_text('''
[project]
name = "pkg"
dependencies = [
  "requests>=2.30.0",
  "pydantic>2.0",
]
''')
    return p


@pytest.fixture
def conflict_monorepo(tmp_path: Path) -> Path:
    (tmp_path / "pkg1").mkdir()
    (tmp_path / "pkg1" / "pyproject.toml").write_text(
        '''[tool.poetry.dependencies]
requests = "^2.31.0"'''
    )
    (tmp_path / "pkg2").mkdir()
    (tmp_path / "pkg2" / "pyproject.toml").write_text(
        '''[tool.poetry.dependencies]
requests = "2.25.1"'''    )
    return tmp_path