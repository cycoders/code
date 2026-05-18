from gc_log_analyzer.parser import parse_gc_log

def test_empty_log():
    pauses = parse_gc_log(iter([]))
    assert pauses == []