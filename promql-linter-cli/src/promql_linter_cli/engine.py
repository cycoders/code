from typing import List
from .models import Issue
from .rules import Rule

def lint(expr: str, rules: List[Rule]) -> List[Issue]:
    """Run all rules against expression."""
    # placeholder using promql-parser in real impl
    return []