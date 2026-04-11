"""Test clipboard."""

from unittest.mock import patch
from unicode_picker_tui.clipboard import copy


def test_copy_success(capsys):
    with patch("pyperclip.copy") as mock_copy:
        assert copy("test")
        mock_copy.assert_called_once_with("test")


def test_copy_fail(capsys):
    with patch("pyperclip.copy", side_effect=Exception("fail")):
        assert not copy("test")
        captured = capsys.readouterr()
        assert "Clipboard error" in captured.err
