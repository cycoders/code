import ast
import pytest
from mutation_tester.mutator import MutantWalker, collect_mutants, BinaryFlipTransformer, NegateTransformer
from pathlib import Path


class TestMutantWalker:
    def test_binop_add(self):
        source = "def foo(): return 1 + 2"
        tree = ast.parse(source)
        walker = MutantWalker()
        walker.visit(tree)
        assert len(walker.locations) == 1
        loc = walker.locations[0]
        assert loc["mut_id"] == "add_to_sub"

    def test_if_negate(self):
        source = "def foo(x): if x > 0: pass"
        tree = ast.parse(source)
        walker = MutantWalker()
        walker.visit(tree)
        assert len(walker.locations) >= 1
        loc = [l for l in walker.locations if l["mut_id"] == "negate_if"][0]
        assert loc["transformer_cls"] == NegateTransformer

    def test_collect_mutants(self, tmp_path: Path):
        pyfile = tmp_path / "test.py"
        pyfile.write_text("def foo(): return 1 + 2 * 3")
        mutants = collect_mutants(pyfile)
        assert len(mutants) >= 2  # add and mul


class TestTransformers:
    def test_binary_flip(self):
        source = "def foo(): return 1 + 2"
        tree = ast.parse(source)
        loc = {"lineno": 1, "col_offset": 12, "mut_id": "add_to_sub", "transformer_cls": BinaryFlipTransformer, "new_op": ast.Sub()}
        transformer = BinaryFlipTransformer(loc)
        mutated = transformer.visit(tree)
        assert "1 - 2" in ast.unparse(mutated)

    def test_negate_if(self):
        source = "def foo(x): if x > 0: pass"
        tree = ast.parse(source)
        loc = {"lineno": 1, "col_offset": 13, "mut_id": "negate_if", "transformer_cls": NegateTransformer}
        transformer = NegateTransformer(loc)
        mutated = transformer.visit(tree)
        assert "not (x > 0)" in ast.unparse(mutated)