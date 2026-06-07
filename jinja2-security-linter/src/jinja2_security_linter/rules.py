from typing import List, Callable
from jinja2.nodes import Node, Filter, Const

Finding = Callable[[Node, str], List]

ALL_RULES: List[Finding] = []

def rule(name: str):
    def decorator(fn):
        ALL_RULES.append(fn)
        return fn
    return decorator

@rule("unsafe-filter")
def check_unsafe_filter(node: Node, filename: str) -> List:
    findings = []
    for n in node.find_all(Filter):
        if n.name == "safe":
            findings.append(("unsafe-filter", filename, n.lineno, "Use of |safe bypasses autoescape"))
    return findings