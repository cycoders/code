from typing import List, Protocol

class Rule(Protocol):
    name: str
    def check(self, ast) -> List:
        ...

DEFAULT_RULES: List[Rule] = []