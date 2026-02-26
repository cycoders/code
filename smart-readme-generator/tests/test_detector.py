import json
import pytest
from pathlib import Path

from smart_readme_generator.detector import (
    detect_stacks,
    parse_metadata,
    has_tests,
    detect_project,
)


@pytest.fixture
def tmp_python_fastapi(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[tool.poetry.dependencies]\nfastapi = "^0.104"')
    return tmp_path


@pytest.fixture
def tmp_react(tmp_path: Path):
    pkg = tmp_path / "package.json"
    pkg.write_text('{"dependencies": {"react": "^18.2.0"}}')
    return tmp_path


@pytest.fixture
def tmp_rust(tmp_path: Path):
    cargo = tmp_path / "Cargo.toml"
    cargo.write_text("[package]\nname = \"my-rs\"\n[dependencies]\nactix-web = \"4\"\n")
    return tmp_path


@pytest.fixture
def tmp_no_stack(tmp_path: Path):
    return tmp_path


def test_detect_python_fastapi(tmp_python_fastapi):
    assert "python-fastapi" in detect_stacks(tmp_python_fastapi)


def test_detect_react(tmp_react):
    assert "react" in detect_stacks(tmp_react)


def test_detect_rust(tmp_rust):
    assert "rust" in detect_stacks(tmp_rust)
    assert "actix-web" in detect_stacks(tmp_rust)


def test_detect_no_stack(tmp_no_stack):
    assert detect_stacks(tmp_no_stack) == []


def test_has_tests(tmp_path: Path):
    (tmp_path / "tests").mkdir()
    assert has_tests(tmp_path)

    # Cleanup
    (tmp_path / "tests").rmdir()
    assert not has_tests(tmp_path)


def test_parse_metadata_pyproject(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[tool.poetry]\nname=\"testproj\"\ndescription=\"Test desc\"")
    name, desc = parse_metadata(tmp_path)
    assert name == "testproj"
    assert desc == "Test desc"


def test_detect_project_full(tmp_python_fastapi):
    data = detect_project(tmp_python_fastapi)
    assert data["stacks"]
    assert data["project_name"]
    assert "FastAPI" in " ".join(data["features"])
