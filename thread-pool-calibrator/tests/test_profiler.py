from thread_pool_calibrator.profiler import LiveProfiler

def test_attach():
    p = LiveProfiler()
    assert "samples" in p.attach(1234)