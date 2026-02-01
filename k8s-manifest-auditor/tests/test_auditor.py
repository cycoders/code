from pathlib import Path
from k8s_manifest_auditor.auditor import audit_path
from k8s_manifest_auditor.types import Issue


def test_audit_path(examples_dir: Path):
    issues = audit_path(examples_dir, "ALL")
    assert len(issues) > 5  # Multiple issues in bad.yaml
    assert any(i.severity == "HIGH" for i in issues)
    assert issues[0].resource.startswith("Deployment")


def test_filter_severity(examples_dir: Path):
    issues = audit_path(examples_dir, "HIGH")
    assert all(i.severity == "HIGH" for i in issues)
