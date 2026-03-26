import sys
from unittest.mock import patch
import domain_profiler_cli.cli as cli_module


@patch("domain_profiler_cli.cli.print_report")
@patch("domain_profiler_cli.profilers.profile_domain")
def test_cli_main(mock_profile, mock_print):
    mock_profile.return_value = {"domain": "test.com"}
    cli_module.main(["test.com"])
    mock_profile.assert_called_once()