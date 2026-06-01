import ast
import pytest
from deadlock_analyzer.analyzer import DeadlockAnalyzer

def test_simple_acquire_order():
    code = '''
with lock1:
    with lock2:
        pass
'''
    tree = ast.parse(code)
    res = DeadlockAnalyzer().analyze(tree)
    assert len(res.edges) == 1

def test_no_cycle_on_linear_order():
    code = "with lock1: pass\nwith lock2: pass"
    tree = ast.parse(code)
    res = DeadlockAnalyzer().analyze(tree)
    assert len(res.cycles) == 0

def test_detects_simple_cycle():
    code = '''
with lock1:
    with lock2: pass
with lock2:
    with lock1: pass
'''
    tree = ast.parse(code)
    res = DeadlockAnalyzer().analyze(tree)
    assert len(res.cycles) >= 1

def test_handles_nested_contexts():
    code = "with lockA:\n    with lockB:\n        with lockC: pass"
    tree = ast.parse(code)
    res = DeadlockAnalyzer().analyze(tree)
    assert len(res.edges) == 2

def test_empty_file():
    tree = ast.parse("")
    res = DeadlockAnalyzer().analyze(tree)
    assert len(res.edges) == 0 and len(res.cycles) == 0