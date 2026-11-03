from pathlib import Path
import tomllib
from .rules import RULES

def audit_project(root: str):
    root = Path(root).resolve()
    findings = []
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
        for rule in RULES:
            findings.extend(rule(data, root))
    else:
        findings.append({"severity": "error", "message": "pyproject.toml missing"})
    return findings