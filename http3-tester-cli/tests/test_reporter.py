import io
from contextlib import redirect_stdout

import pytest
from rich.console import Console

from http3_tester_cli.reporter import print_results


@pytest.fixture
def mock_results():
    return {
        "http3": {
            "stats": {
                "connect": {"mean": 10, "p95": 12, "stddev": 1},
                "ttfb": {"mean": 20, "p95": 25, "stddev": 2},
                "total": {"mean": 30, "p95": 35, "stddev": 3},
            }
        },
        "http2": {
            "stats": {
                "connect": {"mean": 20, "p95": 25, "stddev": 2},
                "ttfb": {"mean": 40, "p95": 45, "stddev": 3},
                "total": {"mean": 60, "p95": 65, "stddev": 4},
            }
        },
        "runs": 5,
    }


def test_print_table(mock_results, capsys):
    print_results(mock_results, "table")
    captured = capsys.readouterr()
    assert "HTTP/3" in captured.out
    assert "50% faster" in captured.out  # approx


def test_print_json(mock_results):
    f = io.StringIO()
    with redirect_stdout(f):
        print_results(mock_results, "json")
    assert "http3" in f.getvalue()
