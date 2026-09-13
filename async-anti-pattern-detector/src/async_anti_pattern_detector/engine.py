import libcst as cst
from .rules import Finding

class AntiPatternVisitor(cst.CSTVisitor):
    def __init__(self):
        self.findings: list[Finding] = []

    def visit_Call(self, node: cst.Call) -> None:
        if isinstance(node.func, cst.Attribute) and node.func.attr.value == "sleep":
            self.findings.append(Finding(node.lineno or 0, node.column or 0, "BLOCKING_CALL", "high", "time.sleep in async context", "await asyncio.sleep(...)"))