from gc_tuning_advisor.parser import parse_gc_log

def test_parse_basic(sample_log):
    events = parse_gc_log(sample_log)
    assert len(events) == 1
    assert events[0].gen == 0