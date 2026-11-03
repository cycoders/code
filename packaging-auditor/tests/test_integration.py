from packaging_auditor.core import audit_project

def test_end_to_end(sample_project):
    res = audit_project(sample_project)
    assert len(res) == 1  # readme warning only