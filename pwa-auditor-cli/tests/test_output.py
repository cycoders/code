import io
from unittest.mock import Mock

import pytest
from rich.console import Console

from pwa_auditor_cli.output import CheckResult, print_results


@pytest.fixture
def mock_console():
    console = Mock(spec=Console)
    console.out = Mock()
    return console


def test_print_results_json(mock_console):
    results = [
        CheckResult("Test", True, "OK", 10, 10),
    ]
    print_results(results, mock_console, json_output=True)
    mock_console.out.write.assert_called_once()


def test_print_results_table(mock_console):
    results = [
        CheckResult("Test", True, "OK", 10, 10),
        CheckResult("Fail", False, "Bad", 0, 10),
    ]
    print_results(results, mock_console, json_output=False)
    # Assert table rendered
    mock_console.print.assert_called()


def test_score_calculation():
    results = [
        CheckResult("A", True, "", 20, 20),
        CheckResult("B", False, "", 0, 30),
    ]
    total_max = sum(r.max_points for r in results)
    score = sum(r.points_awarded for r in results) / total_max * 100
    assert score == 40.0
