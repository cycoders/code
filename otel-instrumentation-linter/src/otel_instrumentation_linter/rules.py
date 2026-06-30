import astroid
from dataclasses import dataclass

@dataclass
class Finding:
    file: str
    line: int
    message: str

class RuleSet:
    def check_file(self, path):
        with open(path) as f:
            try:
                tree = astroid.parse(f.read(), path=str(path))
            except Exception:
                return []
        findings = []
        # simplified rule: detect missing tracer usage
        if "requests.get" in tree.as_string() and "start_as_current_span" not in tree.as_string():
            findings.append(Finding(str(path), 1, "Missing span around external HTTP call"))
        return findings

RULES = RuleSet()