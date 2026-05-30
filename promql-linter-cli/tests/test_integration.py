def test_full_lint_no_crash():
    from promql_linter_cli.engine import lint
    from promql_linter_cli.rules import DEFAULT_RULES
    assert lint('rate(http_requests[5m])', DEFAULT_RULES) == []