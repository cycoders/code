from config_consistency_checker.reporter import render_report

def test_render_empty():
    assert render_report([]) is not None