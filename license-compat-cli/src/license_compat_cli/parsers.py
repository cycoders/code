from pathlib import Path

def detect_lockfile(root: Path):
    candidates = ["poetry.lock", "package-lock.json", "Cargo.lock", "go.sum"]
    for name in candidates:
        p = root / name
        if p.exists():
            return p
    return None