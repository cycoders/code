import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set
import astroid

def build_call_graph(root_path: Path, excludes: List[str]) -> Dict[str, Set[str]]:
    files = _find_python_files(root_path)
    manager = astroid.MANAGER
    modules = {}
    for file_path in files:
        rel_path = file_path.relative_to(root_path)
        mod_name = rel_path.with_suffix('').as_posix().replace('/', '.')
        try:
            mod = manager.ast_from_file(str(file_path), mod_name)
            modules[mod_name] = mod
        except Exception as e:
            print(f"Warning: skipped {file_path}: {e}", file=sys.stderr)
    graph: Dict[str, Set[str]] = defaultdict(set)
    for mod in modules.values():
        visitor = CallGraphVisitor(graph, excludes)
        visitor.visit(mod)
    return dict(graph)

def _find_python_files(root: Path) -> List[Path]:
    return [p for p in root.rglob("*.py") if not (p.name.startswith("__") or p.parent.name.startswith("__"))]

class CallGraphVisitor(astroid.NodeVisitor):
    def __init__(self, graph: Dict[str, Set[str]], excludes: List[str]):
        self.graph = graph
        self.excludes = set(excludes) | {f"{e}." for e in excludes}
        self.current_funcs: List[str] = []

    def visit_FunctionDef(self, node: astroid.FunctionDef):
        qname = node.qname()
        if self._is_excluded(qname):
            self.generic_visit(node)
            return
        self.current_funcs.append(qname)
        self.generic_visit(node)
        self.current_funcs.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node: astroid.Call):
        if not self.current_funcs:
            self.generic_visit(node)
            return
        caller = self.current_funcs[-1]
        try:
            inferred = node.func.inferred()
            for inf in inferred:
                if isinstance(inf, astroid.Function) and not isinstance(inf, astroid.Builtin):
                    callee = inf.qname()
                    if not self._is_excluded(callee) and callee != caller:
                        self.graph[caller].add(callee)
        except:
            pass  # Inference failures are common/OK
        self.generic_visit(node)

    def _is_excluded(self, qname: str) -> bool:
        return any(qname == ex or qname.startswith(ex) for ex in self.excludes)