def test_default_rules_loaded():
    from promql_linter_cli.rules import DEFAULT_RULES
    assert isinstance(DEFAULT_RULES, list)