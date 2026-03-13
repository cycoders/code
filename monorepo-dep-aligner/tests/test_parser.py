import pytest
from pathlib import Path

from monorepo_dep_aligner.parser import find_pyprojects, parse_package_deps


class TestFindPyprojects:
    def test_finds_in_subdirs(self, tmp_path: Path):
        (tmp_path / "pkg" / "pyproject.toml").parent.mkdir(parents=True)
        assert find_pyprojects(tmp_path) == [tmp_path / "pkg" / "pyproject.toml"]

    def test_empty(self, tmp_path: Path):
        assert find_pyprojects(tmp_path) == []


class TestParsePackageDeps:
    def test_poetry_simple(self, poetry_pyproject: Path):
        deps = parse_package_deps(poetry_pyproject)
        assert deps == {"requests": ["^2.31.0"], "pydantic": [">=2.0"]}

    def test_pep621(self, pep621_pyproject: Path):
        deps = parse_package_deps(pep621_pyproject)
        assert deps == {"requests": [">=2.30.0"], "pydantic": [" >2.0"]}

    def test_invalid_toml(self, tmp_path: Path):
        p = tmp_path / "bad.toml"
        p.write_text("invalid")
        assert parse_package_deps(p) is None

    def test_no_deps(self, tmp_path: Path):
        p = tmp_path / "pyproject.toml"
        p.write_text("[project]")
        assert parse_package_deps(p) is None