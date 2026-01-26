import pytest
from terraform_plan_analyzer.summarizer import summarize_changes, format_summary
from terraform_plan_analyzer.parser import parse_plan_file


def test_summarize_changes(sample_plan):
    plan = parse_plan_file(sample_plan)
    from terraform_plan_analyzer.parser import get_resource_changes
    changes = get_resource_changes(plan)
    summary = summarize_changes(changes)
    assert summary["action_totals"] == {"update": 1, "create": 1, "delete": 1}
    assert "aws_instance" in summary["type_details"]
    assert summary["total_changes"] == 3


def test_format_summary():
    summary = {
        "action_totals": {"create": 2, "update": 1},
        "type_details": {"aws_instance": {"create": 1, "update": 1}},
    }
    formatted = format_summary(summary)
    assert "CREATE: 2" in formatted
    assert "aws_instance" in formatted