from context_propagation_auditor.rules import PropagationRule, Finding

def test_flags_create_task():
    rule = PropagationRule()
    assert rule.check(type('obj', (object,), {'func': type('f', (object,), {'attr': type('a', (object,), {'value': 'create_task'})()})(), 'keywords': [], 'lineno': 10})) is not None