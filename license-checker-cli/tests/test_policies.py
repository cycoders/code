import pytest
from license_checker_cli.policies import classify_license, PERMISSIVE_LICENSES


@pytest.mark.parametrize(
    "license_str,expected",
    [
        ("MIT", "permissive"),
        ("Apache-2.0", "permissive"),
        ("GPL-3.0", "copyleft"),
        ("Proprietary", "proprietary"),
        ("Unknown", "unknown"),
    ],
)
def test_classify_license(license_str, expected):
    assert classify_license(license_str) == expected


def test_permissive_set():
    assert "MIT" in PERMISSIVE_LICENSES