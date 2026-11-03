import pytest
from packaging_auditor.core import audit_project

def test_missing_pyproject(tmp_path):
    res = audit_project(tmp_path)
    assert any("missing" in f["message"] for f in res)

def test_valid_minimal(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "0.1"')
    res = audit_project(tmp_path)
    assert not any(f["severity"] == "error" for f in res)