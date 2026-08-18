from thread_pool_calibrator.reporter import render_recommendation

def test_render():
    t = render_recommendation({"optimal": 16})
    assert "16" in str(t)