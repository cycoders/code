from Levenshtein import distance, jaro_winkler
import re
from pathlib import Path

def load_packages(path: Path):
    text = path.read_text()
    pkgs = re.findall(r'([a-z0-9_-]+)', text, re.I)
    return [p.lower() for p in pkgs if len(p) > 1]

def scan_requirements(path, threshold=0.82):
    pkgs = load_packages(Path(path))
    findings = []
    for i, a in enumerate(pkgs):
        for b in pkgs[i+1:]:
            sim = max(1 - distance(a, b) / max(len(a), len(b)), jaro_winkler(a, b))
            if sim >= threshold:
                findings.append({'pair': (a, b), 'score': round(sim, 4)})
    return findings