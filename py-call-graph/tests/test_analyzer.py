import astroid
from collections import defaultdict
from typing import Set

import pytest
from py_call_graph.analyzer import CallGraphVisitor

@pytest.fixture
def empty_graph():
    return defaultdict(set)


def test_simple_function_call(empty_graph):
    code = """
def foo():
    bar()

def bar():
    pass
"""
    mod = astroid.parse(code, "testmod")
    visitor = CallGraphVisitor(empty_graph, [])
    visitor.visit(mod)
    assert 'testmod.foo' in empty_graph
    assert 'testmod.bar' in empty_graph['testmod.foo']


def test_method_call(empty_graph):
    code = """
class A:
    def meth(self):
        self.meth2()

    def meth2(self):
        pass
"""
    mod = astroid.parse(code, "testmod")
    visitor = CallGraphVisitor(empty_graph, [])
    visitor.visit(mod)
    assert 'testmod.A.meth' in empty_graph
    assert 'testmod.A.meth2' in empty_graph['testmod.A.meth']


def test_builtin_ignored(empty_graph):
    code = """
def foo():
    print('hi')
    len([])
    open('f')
"""
    mod = astroid.parse(code, "testmod")
    visitor = CallGraphVisitor(empty_graph, [])
    visitor.visit(mod)
    assert empty_graph['testmod.foo'] == set()


def test_nested_function(empty_graph):
    code = """
def outer():
    def inner():
        pass
    inner()
"""
    mod = astroid.parse(code, "testmod")
    visitor = CallGraphVisitor(empty_graph, [])
    visitor.visit(mod)
    assert 'testmod.outer.<locals>.inner' in empty_graph['testmod.outer']


def test_exclude(empty_graph):
    code = """
def foo():
    bar()

def bar():
    pass
"""
    mod = astroid.parse(code, "testmod")
    visitor = CallGraphVisitor(empty_graph, ['bar'])
    visitor.visit(mod)
    assert empty_graph['testmod.foo'] == set()