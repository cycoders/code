import io
import sys
from unittest.mock import patch
from license_checker_cli.output import print_report
from license_checker_cli.models import LicenseInfo


def test_print_report_table():
    deps = [
        LicenseInfo(name="test", version="1.0", license="MIT", classification="permissive", approved=True)
    ]
    with patch("sys.stdout") as mock_stdout:
        print_report(deps, "table")
        assert "test" in mock_stdout.write.call_args_list[0][0][0]


def test_print_report_json():
    deps = [LicenseInfo(name="test", version="1.0", license="MIT")]
    with patch("sys.stdout"):
        print_report(deps, "json")
