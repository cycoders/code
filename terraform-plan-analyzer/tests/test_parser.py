import pytest
from pathlib import Path
from terraform_plan_analyzer.parser import parse_plan_file, get_resource_changes, get_action


def test_parse_valid_plan(sample_plan: Path):
    plan = parse_plan_file(sample_plan)
    assert "resource_changes" in plan
    assert len(plan["resource_changes"]) == 3


def test_get_resource_changes(sample_plan: Path):
    plan = parse_plan_file(sample_plan)
    changes = get_resource_changes(plan)
    assert len(changes) == 3
    assert changes[0]["address"] == "aws_instance.example"


def test_get_action():
    change_update = {
        "change": {"actions": ["update"]}
    }
    assert get_action(change_update) == "update"

    change_delete = {"change": {"actions": ["delete"]}}
    assert get_action(change_delete) == "delete"

    change_multi = {"change": {"actions": ["create", "read"]}}
    assert get_action(change_multi) == "create,read"


def test_parse_invalid_json(invalid_plan: Path):
    with pytest.raises(ValueError, match="Invalid JSON"):
        parse_plan_file(invalid_plan)


def test_parse_no_resource_changes(tmp_path: Path):
    p = tmp_path / "no_changes.json"
    p.write_text('{"foo": "bar"}')
    with pytest.raises(ValueError, match="missing 'resource_changes'"):
        parse_plan_file(p)