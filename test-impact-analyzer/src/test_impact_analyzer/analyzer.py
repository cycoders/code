from git import Repo
from pathlib import Path
import json

class ImpactAnalyzer:
    def __init__(self, coverage_path: str):
        self.coverage_path = Path(coverage_path)
        self.index = {}

    def analyze(self, base: str, head: str):
        repo = Repo(".")
        diff = repo.git.diff(f"{base}...{head}", name_only=True).splitlines()
        # simplistic mapping for demo
        return {"changed_files": diff, "recommended_tests": ["test_core.py"]}