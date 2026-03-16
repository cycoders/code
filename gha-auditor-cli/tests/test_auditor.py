import pytest
from pathlib import Path
import yaml

from gha_auditor_cli.auditor import audit_directory, _audit_file
from gha_auditor_cli.rules import get_all_rules


@pytest.mark.parametrize("file_name", ["good.yml", "bad.yml"])
def test_auditor(sample_workflows_dir: Path, file_name: str):
    wf_file = sample_workflows_dir / file_name
    issues = _audit_file(wf_file)
    assert isinstance(issues, list)


def test_no_workflows_dir(tmp_path: Path):
    issues = audit_directory(tmp_path)
    assert issues == []


@pytest.mark.parametrize("ext", ["yml", "yaml"])
def test_workflow_discovery(tmp_path: Path, ext):
    wf_path = tmp_path / ".github" / "workflows" / f"test.{ext}"
    wf_path.parent.mkdir(parents=True)
    wf_path.write_text("name: test")
    issues = audit_directory(tmp_path)
    assert len(issues) == 0  # valid empty


def test_invalid_yaml(tmp_path: Path):
    wf_path = tmp_path / ".github" / "workflows" / "invalid.yml"
    wf_path.parent.mkdir(parents=True)
    wf_path.write_text("invalid: yaml")
    issues = audit_directory(tmp_path)
    assert any(i.rule == "parse-error" for i in issues)
