import json
from pathlib import Path
import tomlkit
import pytest
from dep_tree_viz.parsers import _parse_poetry, _parse_npm, _parse_cargo


@pytest.fixture
def mock_paths(tmp_path):
    lock = tmp_path / "lock"
    manifest = tmp_path / "manifest"
    lock.touch()
    manifest.touch()
    return lock, manifest


def test_parse_poetry(mock_paths):
    lock_path, pyproject_path = mock_paths
    lock_path.write_text('''
[[package]]
name = "root"
version = "1.0"
dependencies = [{child = "*"}]

[[package]]
name = "child"
version = "2.0"
dependencies = []
''')
    pyproject_path.write_text('''
[tool.poetry.dependencies]
root = "^1.0"
''')

    roots, graph = _parse_poetry(lock_path, pyproject_path)
    assert roots == ["root@1.0"]
    assert graph["root@1.0"] == ["child@2.0"]
    assert "child@2.0" in graph


def test_parse_npm(mock_paths):
    lock_path, package_json_path = mock_paths
    lock_path.write_text(json.dumps({
        "packages": {
            "": {"name": "root", "version": "1.0", "dependencies": {"child": "node_modules/child"}},
            "node_modules/child": {"name": "child", "version": "2.0"}
        }
    }))
    package_json_path.write_text('{"dependencies": {"child": "^2.0"}}')

    roots, graph = _parse_npm(lock_path, package_json_path, include_dev=False)
    assert roots == ["child@2.0"]
    assert graph["root@1.0"] == ["child@2.0"]


def test_parse_cargo(mock_paths):
    lock_path, cargo_toml_path = mock_paths
    lock_path.write_text('''
[[package]]
name = "root"
version = "1.0"
dependencies = ["child"]

[[package]]
name = "child"
version = "2.0"
dependencies = []
''')
    cargo_toml_path.write_text('''
[dependencies]
child = "2.0"
''')

    roots, graph = _parse_cargo(lock_path, cargo_toml_path, include_dev=False)
    assert roots == ["child@2.0"]
    assert graph["root@1.0"] == ["child@2.0"]


def test_no_manifest_uses_fallback(mock_paths):
    lock_path, _ = mock_paths
    lock_path.write_text('''
[[package]]
name = "root"
version = "1.0"
dependencies = []
''')
    roots, _ = _parse_poetry(lock_path, None)
    assert roots == ["root@1.0"]