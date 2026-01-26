import pytest
from terraform_plan_analyzer.risks import assess_risks
from terraform_plan_analyzer.parser import parse_plan_file, get_resource_changes


def test_assess_risks(sample_plan):
    plan = parse_plan_file(sample_plan)
    changes = get_resource_changes(plan)
    risks = assess_risks(changes)
    assert len(risks) >= 1  # prod delete triggers
    assert "prod" in " ".join(risks)
    assert "🚨" in risks[0]


def test_no_risks(tmp_path):
    # Safe change
    safe_data = {
        "resource_changes": [{
            "address": "aws_instance.dev",
            "type": "aws_instance",
            "change": {"actions": ["update"], "after": {"public_ip": False}},
        }],
    }
    p = tmp_path / "safe.json"
    p.write_text(str(safe_data))
    plan = parse_plan_file(p)
    changes = get_resource_changes(plan)
    risks = assess_risks(changes)
    assert len(risks) == 0