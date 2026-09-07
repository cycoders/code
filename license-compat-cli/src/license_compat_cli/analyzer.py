from pathlib import Path
from .parsers import detect_lockfile
from .matrix import CompatibilityMatrix

class AnalysisResult:
    def __init__(self, conflicts):
        self.conflicts = conflicts
    def render(self):
        print("Conflicts found:", len(self.conflicts))
    def json(self):
        return {"conflicts": self.conflicts}

def analyze_project(root: str):
    root = Path(root)
    lock = detect_lockfile(root)
    if not lock:
        raise SystemExit("No supported lockfile found")
    matrix = CompatibilityMatrix()
    conflicts = matrix.check(lock)
    return AnalysisResult(conflicts)