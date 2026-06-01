import ast
from typing import List, Dict, Set
from .models import LockNode, LockEdge, AnalysisResult

class DeadlockAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.edges: List[LockEdge] = []
        self.current_locks: List[LockNode] = []
        self.lock_names: Dict[str, str] = {}

    def visit_With(self, node: ast.With):
        for item in node.items:
            if isinstance(item.context_expr, ast.Call):
                if isinstance(item.context_expr.func, ast.Attribute) and item.context_expr.func.attr in ('acquire', 'locked'):
                    lock_name = ast.unparse(item.context_expr.func.value)
                    node_obj = LockNode(name=lock_name, location=f"{node.lineno}:{node.col_offset}")
                    if self.current_locks:
                        self.edges.append(LockEdge(self.current_locks[-1], node_obj, node_obj.location))
                    self.current_locks.append(node_obj)
        self.generic_visit(node)
        if self.current_locks:
            self.current_locks.pop()

    def analyze(self, tree: ast.AST) -> AnalysisResult:
        self.visit(tree)
        cycles = self._find_cycles()
        return AnalysisResult(cycles=cycles, edges=self.edges)

    def _find_cycles(self) -> List[List[LockNode]]:
        # Simple DFS cycle detection
        graph: Dict[str, List[LockNode]] = {}
        for e in self.edges:
            graph.setdefault(e.from_node.name, []).append(e.to_node)
        visited: Set[str] = set()
        rec: Set[str] = set()
        cycles = []
        def dfs(n: str, path: List[LockNode]):
            if n in rec:
                idx = [x.name for x in path].index(n)
                cycles.append(path[idx:])
                return
            if n in visited: return
            visited.add(n)
            rec.add(n)
            for nei in graph.get(n, []):
                dfs(nei.name, path + [nei])
            rec.remove(n)
        for node in graph:
            dfs(node, [LockNode(node, "")])
        return cycles