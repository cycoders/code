import json
import pytest
from pathlib import Path
from terraform_plan_analyzer.parser import parse_plan_file


@pytest.fixture
def sample_plan(tmp_path: Path):
    """Minimal valid Terraform plan JSON."""
    data = {
        "format_version": "1.1",
        "resource_changes": [
            {
                "address": "aws_instance.example",
                "type": "aws_instance",
                "name": "example",
                "provider_name": "registry.terraform.io/hashicorp/aws",
                "change": {
                    "actions": ["update"],
                    "before": {"ami": "ami-old"},
                    "after": {"ami": "ami-new"},
                },
            },
            {
                "address": "aws_s3_bucket.prod",
                "type": "aws_s3_bucket",
                "name": "prod",
                "provider_name": "registry.terraform.io/hashicorp/aws",
                "change": {
                    "actions": ["create"],
                    "after": {"acl": "private"},
                },
            },
            {
                "address": "aws_security_group.prod",
                "type": "aws_security_group",
                "name": "prod",
                "provider_name": "registry.terraform.io/hashicorp/aws",
                "change": {
                    "actions": ["delete"],
                    "before": {"public_ip": True},
                },
            },
        ],
    }
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(data))
    return plan_path


@pytest.fixture
def invalid_plan(tmp_path: Path):
    plan_path = tmp_path / "invalid.json"
    plan_path.write_text("{}")
    return plan_path