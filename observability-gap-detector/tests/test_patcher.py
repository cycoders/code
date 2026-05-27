from observability_gap_detector.patcher import generate_patch

def test_patch_is_actionable():
    assert "TODO" in generate_patch("foo")