import pytest
from web_vitals_cli.budget import evaluate_budget
from web_vitals_cli.types import PerfBudget, LighthouseResult, Metric


def test_evaluate_budget(sample_result):
    budget = PerfBudget(lcp=3.0, inp=300, cls=0.2)
    status = evaluate_budget(sample_result, budget)
    assert status["LCP"] == "pass"
    assert status["CLS"] == "pass"


def test_budget_fail(sample_result):
    budget = PerfBudget(lcp=1.0)
    status = evaluate_budget(sample_result, budget)
    assert status["LCP"] == "fail"