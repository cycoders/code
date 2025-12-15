import ast
import pytest
from pathlib import Path

from deadcode_hunter.analyzer import analyze_file, ModuleLevelVisitor, ImportVisitor


SAMPLE_UNUSED_IMPORT = """
import unused_mod  # unused
x = 1  # assigned, unused

def used_func():
    pass

unused_func = lambda: None  # def unused
"""

SAMPLE_USED = """
import os
os.path.join()

def foo():
    pass
foo()
"""


@pytest.fixture
def temp_file(tmp_path: Path, source: str):
    p = tmp_path / "test.py"
    p.write_text(source)
    return p


def test_analyze_unused_imports(temp_file):
    issues = analyze_file(temp_file)
    assert len(issues) >= 1
    unused_imp = next(i for i in issues if i.issue_type == "unused_import")
    assert unused_imp.name == "unused_mod"
    assert unused_imp.confidence == 90


def test_no_issues_used():
    p = Path("nonexistent")
    issues = analyze_file(p)  # empty
    assert not issues


def test_syntax_error_skipped(tmp_path):
    p = tmp_path / "broken.py"
    p.write_text("broken syntax")
    assert not analyze_file(p)


def test_visitor_defs_loads():
    tree = ast.parse(SAMPLE_UNUSED_IMPORT)
    visitor = ModuleLevelVisitor()
    visitor.visit(tree)
    assert "unused_func" in visitor.defs
    assert "unused_func" not in visitor.loads
    assert "x" in visitor.global_assigned
    assert "x" not in visitor.loads
