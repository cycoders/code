import ast
from pathlib import Path
from typing import List
from .rules import RuleEngine

def analyze(path: str, framework: str, config: str | None) -> List[str]:
    engine = RuleEngine(config)
    violations: List[str] = []
    for py_file in Path(path).rglob("*.py"):
        tree = ast.parse(py_file.read_text())
        violations.extend(engine.check(tree, framework, str(py_file)))
    return violations