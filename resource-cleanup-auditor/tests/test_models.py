from resource_cleanup_auditor.models import Issue

def test_issue_creation():
    i = Issue("a.py", 10, "high", "leak", "use with")
    assert i.severity == "high"