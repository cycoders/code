import io
from unittest.mock import Mock
from sql_schema_diff.differ import DiffResult
from sql_schema_diff.render import render_diff
from sql_schema_diff.schema import Schema, Table


def test_render_no_diff(capsys):
    diff = DiffResult({}, {}, {})
    console = Mock()
    render_diff(diff, "table", console)
    captured = capsys.readouterr()
    assert "No schema differences found" in captured.out


def test_render_json(capsys):
    diff = DiffResult({}, {"test": Table("test")}, {})
    render_diff(diff, "json", Mock())
    captured = capsys.readouterr()
    assert '"removed_tables":' in captured.out
