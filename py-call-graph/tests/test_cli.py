import pytest


def test_help(invoke):
    result = invoke(['--help'])
    assert result.exit_code == 0
    assert 'analyze' in result.stdout


def test_stats(invoke, tmp_path):
    p = tmp_path / 'test.py'
    p.write_text('def foo(): pass')
    result = invoke(['analyze', str(p)])
    assert result.exit_code == 0