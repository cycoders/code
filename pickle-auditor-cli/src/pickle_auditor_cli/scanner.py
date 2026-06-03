import libcst as cst
from pathlib import Path
from typing import List
from .rules import UNSAFE_PATTERNS

class Finding:
    def __init__(self, file, line, severity, message):
        self.file, self.line, self.severity, self.message = file, line, severity, message

def scan_directory(root: str, config_path: str | None = None) -> List[Finding]:
    findings = []
    for pyfile in Path(root).rglob("*.py"):
        try:
            tree = cst.parse_module(pyfile.read_text())
            for node in cst.walk(tree):
                if isinstance(node, cst.Call):
                    for pattern in UNSAFE_PATTERNS:
                        if pattern.matches(node):
                            findings.append(Finding(str(pyfile), node.lineno, pattern.severity, pattern.message))
        except Exception:
            pass
    return findings