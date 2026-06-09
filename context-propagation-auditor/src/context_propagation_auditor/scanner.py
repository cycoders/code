from pathlib import Path
import libcst as cst
from .rules import PropagationRule

class Scanner(cst.CSTVisitor):
    def __init__(self):
        self.findings = []
        self.rules = [PropagationRule()]

    def visit_Call(self, node):
        for rule in self.rules:
            if issue := rule.check(node):
                self.findings.append(issue)

def scan_directory(root: str):
    findings = []
    for py in Path(root).rglob("*.py"):
        try:
            tree = cst.parse_module(py.read_text())
            scanner = Scanner()
            tree.walk(scanner)
            findings.extend(scanner.findings)
        except Exception:
            pass
    return findings