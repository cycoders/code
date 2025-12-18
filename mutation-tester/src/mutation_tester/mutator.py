import ast
from typing import List, Iterator

from .types import MutantLocation


binary_mutations = [
    {"name": "add_to_sub", "cond": lambda op: isinstance(op, ast.Add), "new_op": ast.Sub},
    {"name": "sub_to_add", "cond": lambda op: isinstance(op, ast.Sub), "new_op": ast.Add},
    {"name": "mul_to_div", "cond": lambda op: isinstance(op, ast.Mult), "new_op": ast.Div},
    {"name": "div_to_mul", "cond": lambda op: isinstance(op, ast.Div), "new_op": ast.Mult},
]


class MutantWalker(ast.NodeVisitor):
    """AST visitor to collect mutation locations."""

    def __init__(self):
        self.locations: List[MutantLocation] = []

    def record(
        self,
        lineno: int,
        col_offset: int,
        mut_id: str,
        transformer_cls: type,
        **kwargs,
    ):
        loc: MutantLocation = {
            "lineno": lineno,
            "col_offset": col_offset,
            "mut_id": mut_id,
            "transformer_cls": transformer_cls,
            **kwargs,
        }
        self.locations.append(loc)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        for m in binary_mutations:
            if m["cond"](node.op):
                self.record(
                    node.lineno,
                    node.col_offset,
                    m["name"],
                    BinaryFlipTransformer,
                    new_op=m["new_op"](),
                )
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self.record(node.test.lineno, node.test.col_offset, "negate_if", NegateTransformer)
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.record(node.test.lineno, node.test.col_offset, "negate_while", NegateTransformer)
        self.generic_visit(node)


class BinaryFlipTransformer(ast.NodeTransformer):
    """Flips binary operator at target location."""

    def __init__(self, mut_loc: MutantLocation):
        self.lineno = mut_loc["lineno"]
        self.col_offset = mut_loc["col_offset"]
        self.new_op = mut_loc["new_op"]

    def visit_BinOp(self, node: ast.BinOp) -> ast.BinOp:
        if node.lineno == self.lineno and node.col_offset == self.col_offset:
            node.op = self.new_op
        self.generic_visit(node)
        return node


class NegateTransformer(ast.NodeTransformer):
    """Negates condition at target location."""

    def __init__(self, mut_loc: MutantLocation):
        self.lineno = mut_loc["lineno"]
        self.col_offset = mut_loc["col_offset"]

    def visit_If(self, node: ast.If) -> ast.If:
        if node.test.lineno == self.lineno and node.test.col_offset == self.col_offset:
            new_test = ast.UnaryOp(op=ast.Not(), operand=node.test)
            return ast.copy_location(ast.If(test=new_test, body=node.body, orelse=node.orelse), node)
        self.generic_visit(node)
        return node

    def visit_While(self, node: ast.While) -> ast.While:
        if node.test.lineno == self.lineno and node.test.col_offset == self.col_offset:
            new_test = ast.UnaryOp(op=ast.Not(), operand=node.test)
            return ast.copy_location(ast.While(test=new_test, body=node.body, orelse=node.orelse), node)
        self.generic_visit(node)
        return node


def collect_mutants(pyfile: Path) -> List[MutantLocation]:
    """Collect all mutant locations in a file."""
    source = pyfile.read_text(errors="ignore")
    tree = ast.parse(source)
    walker = MutantWalker()
    walker.visit(tree)
    return walker.locations