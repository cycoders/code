import pytest
from merge_risk_analyzer.predictor import RiskPredictor


class TestRiskPredictor:
    def test_compute_risk_score_low(self):
        score, level, sugg = RiskPredictor._compute_risk_score(0.2, 0)
        assert score == 0.2
        assert level == "low"
        assert "Safe" in sugg

    def test_compute_risk_score_medium(self):
        score, level, sugg = RiskPredictor._compute_risk_score(0.4, 5)
        assert 0.4 <= score <= 0.8
        assert level == "medium"
        assert "Review" in sugg

    def test_compute_risk_score_high_capped(self):
        score, level, sugg = RiskPredictor._compute_risk_score(1.5, 50)
        assert score == 1.0
        assert level == "high"
        assert "Rebase" in sugg

    def test_compute_overlap(self):
        ratio, size = RiskPredictor._compute_overlap(100, 400)
        import math
        assert math.isclose(ratio, math.sqrt(40000) / 1000)
        assert size == 500

    def test_analyze_empty_overlap(self, mocker):
        # Minimal mock
        class MockGC:
            def get_merge_base(self, *a): return "base"
            def get_changed_files(self, *a): return set()
        risks = RiskPredictor.analyze(MockGC(), "src", "tgt")
        assert len(risks) == 0
