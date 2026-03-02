import io
from unittest.mock import Mock

import pytest
from rich.console import Console

from port_scanner_cli.output import output_results


@pytest.fixture
def sample_results():
    return [
        {
            "ip": "127.0.0.1",
            "port": 80,
            "open": True,
            "service": "HTTP (nginx)",
            "banner": "nginx/1.25.3",
            "duration": 0.12,
        }
    ]


def test_output_table(sample_results, capsys):
    console = Console(file=io.StringIO())
    output_results(sample_results, "table", console)
    captured = capsys.readouterr()
    assert "HTTP (nginx)" in captured.out


def test_output_json(sample_results, capsys):
    output_results(sample_results, "json", Mock())
    captured = capsys.readouterr()
    assert '"service": "HTTP (nginx)"' in captured.out


def test_output_no_opens(capsys):
    console = Console(file=io.StringIO())
    output_results([], "table", console)
    captured = capsys.readouterr()
    assert "No open ports found" in captured.out