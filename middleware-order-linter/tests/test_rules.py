from middleware_order_linter.rules import RuleEngine

def test_rule_engine_initializes():
    engine = RuleEngine()
    assert engine.rules