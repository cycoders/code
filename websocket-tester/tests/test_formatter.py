import json
from unittest.mock import patch

import pytest
from rich.console import Console
from websocket_tester.formatter import format_payload


@pytest.mark.parametrize(
    "payload,expected",
    [
        ('{"key": "value"}', "key"),
        ("plain text", "plain"),
        ({"a": 1}, "a"),
        ("---\nkey: value\n...", "key"),
    ],
)
def test_format_payload(capsys, payload, expected):
    format_payload(payload)
    captured = capsys.readouterr()
    assert expected in captured.out


@patch.object(Console, "print")
def test_format_repr(mock_print, capsys):
    format_payload(42)
    mock_print.assert_called_once()
    captured = capsys.readouterr()
    assert "42" in captured.out