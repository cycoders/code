import math
from pathlib import Path

def shannon_entropy(s: str) -> float:
    if not s: return 0.0
    freq = {}
    for c in s: freq[c] = freq.get(c, 0) + 1
    return -sum((c/len(s))*math.log2(c/len(s)) for c in freq.values())

def scan_path(root: str, min_entropy: float):
    findings = []
    for p in Path(root).rglob("*"):
        if p.is_file() and p.suffix in {'.py','.js','.yaml','.env'}:
            text = p.read_text(errors='ignore')
            for line in text.splitlines():
                for token in line.split():
                    if len(token) > 12 and shannon_entropy(token) >= min_entropy:
                        findings.append({'file': str(p), 'token': token[:8]+'...'})
    return findings