from observability_gap_detector.scoring import score_gap

def test_handler_scores_higher():
    assert score_gap("handler") > score_gap("helper")