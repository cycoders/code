import pytest
from gha_auditor_cli.issue import Issue
from gha_auditor_cli.rules import (
    rule_unpinned_actions,
    rule_hardcoded_secrets,
    rule_broad_permissions,
    rule_missing_permissions,
    rule_insecure_checkout,
    rule_missing_cache,
)


@pytest.mark.parametrize(
    "data, expected_count",
    [
        (
            {"jobs": {"build": {"steps": [{"uses": "actions/checkout"}]}}},  # unpinned
            1,
        ),
        (
            {"jobs": {"build": {"steps": [{"uses": "actions/checkout@v4"}]}}},  # pinned
            0,
        ),
        (
            {"jobs": {"build": {"steps": [{"uses": "actions/checkout@latest"}]}}},  # floating
            1,
        ),
    ],
)
def test_unpinned_actions(data, expected_count):
    issues = rule_unpinned_actions(data, "test.yml")
    assert len(issues) == expected_count


@pytest.mark.parametrize(
    "run_text, expected",
    [
        ('echo "password=foo"', 1),
        ('export API_KEY=bar', 1),
        ('${{ secrets.PASS }}', 0),
        ('normal command', 0),
    ],
)
def test_hardcoded_secrets(run_text):
    data = {"jobs": {"build": {"steps": [{"run": run_text}]}}}
    issues = rule_hardcoded_secrets(data, "test.yml")
    assert len(issues) == run_text.count("=")  # simplistic


@pytest.mark.parametrize(
    "data, expected_count",
    [
        ({"permissions": {"*": "write"}}, 1),
        ({"permissions": {"contents": "read"}}, 0),
    ],
)
def test_broad_permissions(data, expected_count):
    issues = rule_broad_permissions(data, "test.yml")
    assert len(issues) == expected_count


@pytest.mark.parametrize(
    "data, expected_count",
    [
        ({}, 1),  # missing
        ({"permissions": {}}, 0),
    ],
)
def test_missing_permissions(data, expected_count):
    issues = rule_missing_permissions(data, "test.yml")
    assert len(issues) == expected_count


@pytest.mark.parametrize(
    "data, expected_count",
    [
        (
            {
                "jobs": {
                    "deploy": {
                        "permissions": {"contents": "write"},
                        "steps": [{"uses": "actions/checkout@v4"}],
                    }
                }
            },
            1,  # insecure
        ),
        (
            {
                "jobs": {
                    "deploy": {
                        "permissions": {"contents": "write"},
                        "steps": [
                            {"uses": "actions/checkout@v4", "with": {"token": "${{ secrets.GITHUB_TOKEN }}"}}
                        ],
                    }
                }
            },
            0,
        ),
    ],
)
def test_insecure_checkout(data, expected_count):
    issues = rule_insecure_checkout(data, "test.yml")
    assert len(issues) == expected_count


@pytest.mark.parametrize(
    "data, expected_count",
    [
        ({"jobs": {"build": {"steps": [{"uses": "actions/setup-node@v4"}]}}}, 1),
        (
            {
                "jobs": {
                    "build": {"steps": [{"uses": "actions/setup-node@v4", "with": {"cache": "npm"}}]}
                }
            },
            0,
        ),
    ],
)
def test_missing_cache(data, expected_count):
    issues = rule_missing_cache(data, "test.yml")
    assert len(issues) == expected_count
