from gc_tuning_advisor.parser import parse_gc_log
from gc_tuning_advisor.analyzer import analyze

def test_full_pipeline(sample_log):
    events = parse_gc_log(sample_log)
    assert analyze(events)