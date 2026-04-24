from typing import Any, Dict, List, Set
from ariadne import Schema

from .rules import (
    check_naming,
    check_deprecations,
    check_types,
    check_design,
    check_perf,
    check_security,
)


Issue = Dict[str, Any]


class Auditor:
    def __init__(self, schema: Schema, ignore_rules: Set[str] = None):
        self.schema = schema
        self.ignore_rules = ignore_rules or set()

    def run(self) -> List[Issue]:
        """Run all rules and collect issues."""
        issues: List[Issue] = []
        rules = [
            check_naming,
            check_deprecations,
            check_types,
            check_design,
            check_perf,
            check_security,
        ]
        for rule in rules:
            if rule.__name__ in self.ignore_rules:
                continue
            issues.extend(rule(self.schema))
        return sorted(issues, key=lambda i: (i["severity"], i["path"]))