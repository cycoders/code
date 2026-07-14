from type_snapshot_cli.aggregator import TypeAggregator

def test_single_type():
    agg = TypeAggregator()
    def f(x): pass
    agg.observe(f, {"x": 42})
    assert agg.reduce()["__main__.f:x"] == "int"

def test_union_type():
    agg = TypeAggregator()
    def f(x): pass
    agg.observe(f, {"x": 1})
    agg.observe(f, {"x": "a"})
    assert "int | str" in agg.reduce()["__main__.f:x"]