import ast
from pathlib import Path

import pytest
from py_perf_auditor.analyzer import PerfVisitor, Violation, analyze_file


@pytest.fixture
def bad_string_concat():
    return """
s = ""
for i in range(100):
    s += str(i)
    s = s + "foo"
"""

@pytest.fixture
def good_string_join():
    return """
parts = []
for i in range(100):
    parts.append(str(i))
s = ''.join(parts)
"""


class TestPerfVisitor:
    def test_string_concat_loop(self, bad_string_concat):
        tree = ast.parse(bad_string_concat)
        visitor = PerfVisitor()
        visitor.visit(tree)
        assert len(visitor.violations) >= 1
        v = visitor.violations[0]
        assert v.rule == "string-concat-loop"
        assert v.severity == "HIGH"

    def test_list_concat(self):
        code = """
l1 = [1,2]
l2 = [3,4]
for i in range(10):
    res = l1 + l2
"""
        tree = ast.parse(code)
        visitor = PerfVisitor()
        visitor.visit(tree)
        assert len(visitor.violations) == 1
        assert visitor.violations[0].rule == "list-concat"

    def test_list_on_map(self):
        code = """
res = list(map(str, range(10)))
for i in range(10):
    lst = list(filter(lambda x: x>0, [-1,1,2]))
"""
        tree = ast.parse(code)
        visitor = PerfVisitor()
        visitor.visit(tree)
        assert len(visitor.violations) == 2
        rules = {v.rule for v in visitor.violations}
        assert "list-on-map-filter" in rules

    def test_list_dict_keys(self):
        code = """
d = {'a':1}
keys = list(d.keys())
for i in range(10):
    lst = list(d.keys())
"""
        tree = ast.parse(code)
        visitor = PerfVisitor()
        visitor.visit(tree)
        assert len(visitor.violations) == 2
        assert all(v.rule == "list-dict-keys" for v in visitor.violations)

    def test_no_false_positives(self, good_string_join):
        tree = ast.parse(good_string_join)
        visitor = PerfVisitor()
        visitor.visit(tree)
        assert len(visitor.violations) == 0


class TestAnalyzeFile:
    def test_valid_py(self, tmp_path: Path):
        p = tmp_path / "test.py"
        p.write_text('print("hello")')
        assert analyze_file(p) == []

    def test_bad_py(self, tmp_path: Path, bad_string_concat):
        p = tmp_path / "bad.py"
        p.write_text(bad_string_concat)
        violations = analyze_file(p)
        assert len(violations) >= 1
        assert violations[0].lineno > 0

    def test_non_py(self, tmp_path: Path):
        p = tmp_path / "test.txt"
        assert analyze_file(p) == []

    def test_syntax_error(self, tmp_path: Path):
        p = tmp_path / "invalid.py"
        p.write_text("def foo(:")
        assert analyze_file(p) == []
