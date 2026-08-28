from pathlib import Path
from typing import List
from crypto_agility_scanner.rules import RULES
from crypto_agility_scanner.models import Finding

def scan_path(root: str) -> List[Finding]:
    findings: List[Finding] = []
    for p in Path(root).rglob("*.py"):
        if p.name.startswith("."): continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for rule in RULES:
            findings.extend(rule.check(p, text))
    return findings