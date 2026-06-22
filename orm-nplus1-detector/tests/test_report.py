from orm_nplus1_detector.report import render_findings

def test_render_empty():
    assert render_findings([]) is not None