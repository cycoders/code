import pytest
from unittest.mock import Mock

from sql_index_suggester.models import IndexSuggestion
from sql_index_suggester.renderer import render_table, render_json


def test_render_table():
    mock_console = Mock()
    sugg = [IndexSuggestion("test", ["col"], 80.0, "CREATE...", "rationale")]
    render_table(mock_console, sugg)
    mock_console.print.assert_called()


def test_render_json():
    sugg = [IndexSuggestion("test", ["col"], 80.0, "CREATE...", "rationale")]
    json_str = render_json(sugg)
    assert '"score": 80.0' in json_str
