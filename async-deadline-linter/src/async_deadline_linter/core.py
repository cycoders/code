from pathlib import Path
import libcst as cst
from .visitor import DeadlineVisitor

def analyze(root: str):
    findings = []
    for py in Path(root).rglob("*.py"):
        tree = cst.parse_module(py.read_text())
        v = DeadlineVisitor()
        tree.walk(v)
        findings.extend(v.findings)
    return findings