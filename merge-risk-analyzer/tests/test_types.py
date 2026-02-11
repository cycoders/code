from merge_risk_analyzer.types import FileRisk


def test_filerisk_dataclass():
    risk = FileRisk(
        path="test.py",
        overlap_ratio=0.5,
        change_size=100,
        historical_conflicts=5,
        risk_score=0.75,
        risk_level="high",
        suggestion="Rebase",
    )
    assert risk.path == "test.py"
    assert risk.risk_score == 0.75
