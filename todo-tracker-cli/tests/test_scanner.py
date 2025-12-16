import pytest
from pathlib import Path

from todo_tracker_cli.scanner import scan, TodoItem


def test_scan_py(tmp_path: Path, sample_py_file):
    todos = list(scan(tmp_path, []))
    assert len(todos) == 2
    assert todos[0].tag == 'TODO'
    assert todos[0].filepath.endswith('test.py')
    assert todos[0].line == 1


@pytest.mark.parametrize('suffix,expected', [
    ('.py', True),
    ('.js', True),
    ('.txt', False),
])
def test_lang_patterns(tmp_path: Path, suffix, expected):
    p = tmp_path / f'test{suffix}'
    p.write_text('# TODO: test')
    todos = list(scan(tmp_path, []))
    assert bool(todos) == expected


def test_ignore_globs(tmp_path: Path):
    ignore_file = tmp_path / 'venv' / 'test.py'
    ignore_file.parent.mkdir()
    ignore_file.write_text('# TODO')
    todos = list(scan(tmp_path, ['venv/**']))
    assert len(todos) == 0


def test_custom_tags(tmp_path: Path):
    p = tmp_path / 'test.py'
    p.write_text('# OPTIMIZE: Better algo')
    todos = list(scan(tmp_path, [], ['OPTIMIZE']))
    assert len(todos) == 1
    assert todos[0].tag == 'OPTIMIZE'