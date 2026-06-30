from otel_instrumentation_linter.rules import RULES, Finding

def test_rule_set_initializes():
    assert RULES is not None