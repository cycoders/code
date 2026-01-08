import ast
from pathlib import Path
from textwrap import dedent

from py_api_diff.models import ApiElement, ArgSig
from py_api_diff.parser import parse_py_file


SAMPLE_FUNC = """
def public(a, b=1):
    pass

def _private():
    pass
"""

SAMPLE_CLASS = """
class Public:
    def __init__(self, x, y=2):
        pass

class PublicNoInit:
    pass

class _Private:
    pass
"""


class TestParser:
    def test_function_public(self):
        tree = ast.parse(SAMPLE_FUNC)
        elems = list(parse_py_file(SAMPLE_FUNC, "mod"))
        assert len(elems) == 1
        assert elems[0] == ApiElement("mod.public", "function", (ArgSig("a", False), ArgSig("b", True)))

    def test_class_init(self):
        elems = list(parse_py_file(SAMPLE_CLASS, "mod"))
        assert len(elems) == 2
        init_class = next(e for e in elems if e.qualname == "mod.Public")
        assert init_class.arg_sigs == (ArgSig("x", False), ArgSig("y", True))
        noinit = next(e for e in elems if e.qualname == "mod.PublicNoInit")
        assert noinit.arg_sigs == tuple()

    def test_syntax_error_skipped(self):
        bad = "def invalid: pass"
        elems = list(parse_py_file(bad, "mod"))
        assert elems == []

    def test_no_self_skip(self):
        func = "def func(a=1): pass"
        elems = list(parse_py_file(func, "mod"))
        assert elems[0].arg_sigs == (ArgSig("a", True),)