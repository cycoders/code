import libcst as cst
import pytest
from pathlib import Path

from symbol_renamer_cli.renamer import Renamer, process_file
from symbol_renamer_cli.diff_utils import show_preview


class TestRenamer:
    def test_rename_function(self) -> None:
        code = """
def old_func():
    pass

old_func()
"""
        tree = cst.parse_module(code)
        transformer = Renamer("old_func", "new_func")
        new_tree = tree.visit(transformer)
        assert transformer.changes == 2
        assert "new_func" in new_tree.code
        assert "def new_func():" in new_tree.code

    def test_rename_variable(self) -> None:
        code = """
x = 42
print(x)
"""
        tree = cst.parse_module(code)
        transformer = Renamer("x", "y")
        new_tree = tree.visit(transformer)
        assert transformer.changes == 2
        assert "y = 42" in new_tree.code

    def test_rename_class(self) -> None:
        code = """
class MyClass:
    pass

obj = MyClass()
"""
        tree = cst.parse_module(code)
        transformer = Renamer("MyClass", "NewClass")
        new_tree = tree.visit(transformer)
        assert transformer.changes == 2
        assert "NewClass" in new_tree.code

    def test_no_change(self) -> None:
        code = """
def other():
    pass
"""
        tree = cst.parse_module(code)
        transformer = Renamer("missing", "new")
        new_tree = tree.visit(transformer)
        assert transformer.changes == 0
        assert new_tree.code == code

    def test_shadowed_rename_all(self) -> None:
        code = """
global_x = 1

def func():
    local_x = 2
    print(global_x, local_x)

print(global_x)
"""
        tree = cst.parse_module(code)
        transformer = Renamer("global_x", "global_y")
        new_tree = tree.visit(transformer)
        assert transformer.changes == 2
        assert new_tree.code.count("global_y") == 2


class TestProcessFile:
    @pytest.fixture
    def temp_py(self, tmp_path: Path) -> Path:
        p = tmp_path / "test.py"
        p.write_text("def foo(): pass\nfoo()\n")
        return p

    def test_process_preview(self, temp_py: Path, mocker: pytest.MonkeyPatch) -> None:
        mock_console = mocker.Mock(spec=Console)
        mock_show = mocker.patch("symbol_renamer_cli.renamer.show_preview")
        changes = process_file(temp_py, "foo", "bar", mock_console, preview=True)
        assert changes == 2
        mock_show.assert_called_once()
