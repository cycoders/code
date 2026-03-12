import json
import tomllib
from pathlib import Path
from typing import List

import pytest
from osv_dep_scanner.parsers import (
    Dependency,
    detect_lockfile_type,
    parse_lockfile,
)


@pytest.mark.parametrize(
    "name,content,expected_type",
    [
        ("package-lock.json", '{"packages":{}}', "npm"),
        ("poetry.lock", '{"package":[]}', "pypi"),
        ("Cargo.lock", "[[package]]", "crates"),
    ],
)
def test_detect_lockfile_type(tmp_path: Path, name: str, content: str, expected_type: str):
    p = tmp_path / name
    p.write_text(content)
    assert detect_lockfile_type(p) == expected_type


class TestParsers:
    @pytest.mark.parametrize(
        "name,content,expected_deps",
        [
            (
                "package-lock.json",
                '''{"packages":{"node_modules/lodash":{"version":"4.17.21"}}}''',
                [{"ecosystem": "npm", "name": "lodash", "version": "4.17.21"}],
            ),
            (
                "poetry.lock",
                '''{"package":[{"name":"requests","version":"2.32.4"}]}''',
                [{"ecosystem": "PyPI", "name": "requests", "version": "2.32.4"}],
            ),
            (
                "Cargo.lock",
                '''[[package]]\nname="serde"\nversion="1.0.210"''',
                [{"ecosystem": "crates", "name": "serde", "version": "1.0.210"}],
            ),
        ],
    )
    def test_parse_lockfile(self, tmp_path: Path, name: str, content: str, expected_deps: List[Dependency]):
        p = tmp_path / name
        p.write_text(content)
        deps = parse_lockfile(p)
        assert len(deps) >= len(expected_deps)
        for exp in expected_deps:
            assert any(d == exp for d in deps)