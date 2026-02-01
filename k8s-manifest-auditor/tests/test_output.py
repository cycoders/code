def test_no_issues_table(capsys):
    from k8s_manifest_auditor.output import print_table
    from k8s_manifest_auditor.types import Issue
    print_table([])
    captured = capsys.readouterr()
    assert "No issues found" in captured.out
