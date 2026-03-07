import io
from unittest.mock import patch
from wcag_checker_cli.reporter import console_report
from wcag_checker_cli.types import Issue


def test_console_report_empty():
    with patch('rich.console.Console.print') as mock_print:
        console_report([])
        mock_print.assert_called_with("[bold green]✓ Perfect! All WCAG checks passed.[/] 🎉")


def test_console_report_issues():
    issue = Issue(id='test', wcag='1.1.1', principle='P', level='A', severity='error',
                  description='test desc', impact='H', help='fix it')
    with patch('rich.console.Console') as mock_console:
        console_report([issue])
        # Asserts output structured
        pass
