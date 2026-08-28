from config_consistency_checker.policy import validate_policy

def test_valid_policy():
    assert validate_policy({'k':1}, {'type':'object','properties':{'k':{'type':'integer'}}})