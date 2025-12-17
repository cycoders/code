import ast
import pytest

from type_coverage_cli.models import ElementCoverage
from type_coverage_cli.visitor import CoverageVisitor


@pytest.mark.parametrize(
    "code, expected_funcs, expected_typed_funcs, expected_params, expected_typed_params, expected_returns, expected_typed_returns",
    [
        (
            "def foo(a: int) -> str: pass",
            1, 1, 1, 1, 1, 1,
        ),
        (
            "def bar(x): pass",
            1, 0, 1, 0, 1, 0,
        ),
        (
            "def baz(a, b: int) -> None: pass",
            1, 0, 2, 1, 1, 1,
        ),
        (
            "class C: def meth(self: 'C') -> None: pass",
            1, 1, 1, 1, 1, 1,
        ),
        (
            "async def asyncf(a: int) -> int: pass",
            1, 1, 1, 1, 1, 1,
        ),
    ],
)
def test_visitor(code, expected_funcs, expected_typed_funcs, expected_params, expected_typed_params, expected_returns, expected_typed_returns):
    tree = ast.parse(code)
    visitor = CoverageVisitor()
    visitor.visit(tree)
    assert visitor.stats.funcs.total == expected_funcs
    assert visitor.stats.funcs.typed == expected_typed_funcs
    assert visitor.stats.params.total == expected_params
    assert visitor.stats.params.typed == expected_typed_params
    assert visitor.stats.returns.total == expected_returns
    assert visitor.stats.returns.typed == expected_typed_returns


def test_nested_functions():
    code = """
def outer():
    def inner(a: int) -> str:
        pass
    """
    tree = ast.parse(code)
    visitor = CoverageVisitor()
    visitor.visit(tree)
    assert visitor.stats.funcs.total == 2
    assert visitor.stats.funcs.typed == 1