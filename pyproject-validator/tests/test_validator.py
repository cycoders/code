import pytest
from pyproject_validator.validator import validate


def test_missing_name(tmp_path):
    p = tmp_path / "pyproject.toml"
    p.write_text('[project]\nversion = "1.0"')
    assert any("name" in e for e in validate(str(p)))


def test_valid_minimal(tmp_path):
    p = tmp_path / "pyproject.toml"
    p.write_text('[project]\nname = "x"\nversion = "1.0"\n[build-system]\nbuild-backend = "hatchling.build"')
    assert validate(str(p)) == []


def test_missing_backend(tmp_path):
    p = tmp_path / "pyproject.toml"
    p.write_text('[project]\nname = "x"\nversion = "1.0"')
    assert any("build-backend" in e for e in validate(str(p)))