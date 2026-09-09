from sbom_diff_cli.policy import Policy, evaluate

def test_fail_on_critical():
    p = Policy(fail_on_critical=True)
    assert evaluate({}, p) == []