from orm_nplus1_detector.tracer import start_trace

def test_tracer_starts():
    assert start_trace(1) is None