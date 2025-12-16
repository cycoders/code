import io
import sys
from unittest.mock import patch

import pytest
from todo_tracker_cli.reporter import report
from todo_tracker_cli.models import TodoItem


@pytest.mark.parametrize('fmt', ['table', 'csv', 'mermaid'])
def test_report(fmt):
    todos = [
        TodoItem('test.py', 10, 'TODO', 'Fix me', 365.2, 'alice'),
    ]
    with patch('sys.stdout', new=io.StringIO()) as fake_out:
        report(todos, fmt=fmt)
        output = fake_out.getvalue()
        assert 'TODO' in output
        assert 'test.py' in output


def test_empty_report():
    todos = []
    with patch('sys.stdout', new=io.StringIO()):
        report(todos)
        # No crash