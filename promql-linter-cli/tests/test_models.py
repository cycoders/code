from promql_linter_cli.models import Issue

def test_issue_creation():
    i = Issue("error", "bad query")
    assert i.severity == "error"