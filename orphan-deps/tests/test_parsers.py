import pathlib

import pytest
from orphan_deps.parsers import collect_top_level_imports, parse_requirements_file, parse_pyproject


class TestCollectImports:
    def test_basic_imports(self, tmp_path: pathlib.Path):
        (tmp_path / "a.py").write_text("import requests\nfrom flask import g")
        used = collect_top_level_imports(tmp_path)
        assert 'requests' in used
        assert 'flask' in used

    def test_stdlib_exclude(self, tmp_path: pathlib.Path):
        (tmp_path / "b.py").write_text("import os\nfrom sys import argv")
        used = collect_top_level_imports(tmp_path)
        assert 'os' not in used
        assert 'sys' not in used

    def test_exclude_dirs(self, tmp_path: pathlib.Path):
        venv_dir = tmp_path / ".venv / x.py"
        venv_dir.parent.mkdir(parents=True)
        venv_dir.write_text("import foo")
        used = collect_top_level_imports(tmp_path)
        assert len(used) == 0  # Excluded

    def test_syntax_error_skip(self, tmp_path: pathlib.Path):
        (tmp_path / "invalid.py").write_text("def foo(\n")
        used = collect_top_level_imports(tmp_path)
        assert len(used) == 0


class TestParseReqs:
    def test_parse_requirements(self, tmp_path: pathlib.Path):
        reqs = tmp_path / "reqs.txt"
        reqs.write_text("requests # comment\nFlask>=1\n  unused @ git\n# skipped")
        pkgs = parse_requirements_file(reqs)
        assert pkgs == {'requests', 'flask'}


class TestParsePyproject:
    def test_parse_pyproject(self, tmp_path: pathlib.Path):
        toml = tmp_path / "pyproject.toml"
        toml.write_text("[tool.poetry.dependencies]\npython='^3'\nReq=1\n[project.dependencies]\nFlask=1")
        pkgs = parse_pyproject(toml)
        assert pkgs == {'req', 'flask'}