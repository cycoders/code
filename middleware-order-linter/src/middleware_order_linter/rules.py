from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Violation:
    file: str
    line: int
    msg: str

class RuleEngine:
    def __init__(self, config_path: str | None = None):
        self.rules = DEFAULT_RULES  # load yaml if provided

    def check(self, tree, framework: str, filename: str) -> List[str]:
        # simplified rule evaluation
        return []