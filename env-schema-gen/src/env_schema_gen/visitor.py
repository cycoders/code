'''
AST visitor to detect env var usages.

Supports:
- os.getenv('VAR')
- os.getenv('VAR', default)
- os.environ.get('VAR')
- os.environ.get('VAR', default)
- os.environ['VAR']
- Inside lambdas/functions
'''

from collections import defaultdict
from typing import Dict, List, Tuple

import ast


class EnvVarVisitor(ast.NodeVisitor):
    """AST visitor extracting env vars, types, locations."""

    def __init__(self, filename: str) -> None:
        super().__init__()
        self.filename: str = filename
        self.vars: set[str] = set()
        self.locations: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.type_hints: Dict[str, str] = {}

    def visit_Call(self, node: ast.Call) -> None:
        self.generic_visit(node)
        self._check_getenv_call(node)
        self._check_environ_get_call(node)

    def _check_getenv_call(self, node: ast.Call) -> None:
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and func.attr == 'getenv'
            and isinstance(func.value, ast.Name)
            and func.value.id == 'os'
        ):
            self._process_env_arg(node, 0)

    def _check_environ_get_call(self, node: ast.Call) -> None:
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and func.attr == 'get'
            and isinstance(func.value, ast.Attribute)
            and func.value.attr == 'environ'
            and isinstance(func.value.value, ast.Name)
            and func.value.value.id == 'os'
        ):
            self._process_env_arg(node, 0)

    def _process_env_arg(self, node: ast.Call, arg_idx: int) -> None:
        if len(node.args) > arg_idx:
            arg = node.args[arg_idx]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                var_name: str = arg.value
                self.vars.add(var_name)
                self.locations[var_name].append((self.filename, node.lineno or 0))
                if len(node.args) > arg_idx + 1:
                    self._infer_type(var_name, node.args[arg_idx + 1])

    def visit_Subscript(self, node: ast.Subscript) -> None:
        self.generic_visit(node)
        value = node.value
        index = node.slice
        if (
            isinstance(value, ast.Attribute)
            and value.attr == 'environ'
            and isinstance(value.value, ast.Name)
            and value.value.id == 'os'
            and isinstance(index, ast.Index)
            and isinstance(index.value, ast.Constant)
            and isinstance(index.value.value, str)
        ):
            var_name: str = index.value.value
            self.vars.add(var_name)
            self.locations[var_name].append((self.filename, node.lineno or 0))

    def _infer_type(self, var_name: str, default_node: ast.AST) -> None:
        if isinstance(default_node, ast.Constant):
            val = default_node.value
            if isinstance(val, (int, float, str, bool)):
                self.type_hints[var_name] = type(val).__name__