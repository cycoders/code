from context_propagation_auditor.rules import PropagationRule

def test_ignores_safe_calls():
    rule = PropagationRule()
    assert rule.check(type('obj', (object,), {'func': type('f', (object,), {'attr': type('a', (object,), {'value': 'gather'})()})(), 'keywords': [], 'lineno': 1})) is None