from config_consistency_checker.differ import semantic_diff

def test_semantic_diff_ignores_order():
    assert semantic_diff({'a':1,'b':2}, {'b':2,'a':1}) == []