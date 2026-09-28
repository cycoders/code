from dataclasses import dataclass
import ast

@dataclass
class Pattern:
    node_type: type[ast.AST]
    attrs: dict[str, object]

    def matches(self, node: ast.AST) -> bool:
        if not isinstance(node, self.node_type):
            return False
        return all(getattr(node, k, None) == v for k, v in self.attrs.items())