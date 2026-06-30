from pathlib import Path
from .rules import RULES

def scan_path(root: str, config_path: str | None = None):
    findings = []
    for py_file in Path(root).rglob("*.py"):
        if "test_" in py_file.name:
            continue
        findings.extend(RULES.check_file(py_file))
    return findings