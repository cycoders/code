import ast
import logging
from pathlib import Path
from typing import List, Iterator, Optional, Set

from .types import Message

logger = logging.getLogger(__name__)

class Extractor(ast.NodeVisitor):
    """AST visitor to extract translatable strings."""

    def __init__(self, functions: Set[str], plural_functions: Set[str]):
        self.functions = functions
        self.plural_functions = plural_functions
        self.current_file: str = "<unknown>"
        self.messages: List[Message] = []

    def visit_Call(self, node: ast.Call) -> None:
        func_name = self._get_func_name(node.func)
        if func_name in self.functions:
            if node.args:
                template = self._extract_template(node.args[0])
                self.messages.append(Message(template, location=(self.current_file, node.lineno)))
        elif func_name in self.plural_functions and len(node.args) >= 2:
            sing = self._extract_template(node.args[0])
            plur = self._extract_template(node.args[1])
            self.messages.append(Message(sing, plur, (self.current_file, node.lineno)))
        self.generic_visit(node)

    def _get_func_name(self, node: ast.expr) -> Optional[str]:
        if isinstance(node, ast.Name):
            return node.id
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id in {"gettext"}
        ):
            return f"{node.value.id}.{node.attr}"
        return None

    def _extract_template(self, node: Optional[ast.expr]) -> str:
        if not node:
            return ""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.JoinedStr):
            parts: List[str] = []
            for value in node.values:
                part = self._extract_template(value)
                parts.append(part if part else "{}")
            return "".join(parts)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "format"
            and isinstance(node.func.value, ast.Constant)
            and isinstance(node.func.value.value, str)
        ):
            return node.func.value.value
        return "{}"


def scan_file(file_path: Path, functions: Set[str], plural_functions: Set[str]) -> List[Message]:
    """Scan a single Python file for messages."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=str(file_path))
        extractor = Extractor(functions, plural_functions)
        extractor.current_file = str(file_path)
        extractor.visit(tree)
        return extractor.messages
    except SyntaxError as e:
        logger.warning(f"Skipping {file_path}: {e}")
        return []


def scan_paths(paths: List[Path], functions: Set[str], plural_functions: Set[str]) -> Iterator[List[Message]]:
    """Scan multiple paths, yielding per-file messages."""
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            yield scan_file(path, functions, plural_functions)
        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                yield scan_file(py_file, functions, plural_functions)