import pytest
from build_log_analyzer.models import LogSummary, Step


def test_step_model():
    step = Step(name="test step", duration=5.2, status="success")
    assert step.name == "test step"
    assert step.duration == 5.2
    assert step.errors == []


def test_step_validation():
    with pytest.raises(ValueError, match="duration"):
        Step(name="bad", duration=-1)


def test_summary_model():
    summary = LogSummary(filename="test.log", total_duration=42.0)
    assert summary.filename == "test.log"
    assert summary.total_duration == 42.0
    assert len(summary.steps) == 0

    step = Step(name="step1")
    summary.steps.append(step)
    assert len(summary.steps) == 1