from gc_log_analyzer.parser import parse_gc_log

def test_parse_simple():
    lines = ["[0.123s][info][gc] GC(1) Pause Young 12.340ms", "[0.200s][info][gc] GC(2) Pause Old 45.000ms"]
    pauses = parse_gc_log(iter(lines))
    assert len(pauses) == 2
    assert pauses[0].generation == "young"