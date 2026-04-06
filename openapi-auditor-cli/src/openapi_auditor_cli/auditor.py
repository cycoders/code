from typing import List

from .models import Issue
from .rules.design import DesignRules
from .rules.security import SecurityRules
from .rules.performance import PerformanceRules


class Auditor:
    """Core auditor that runs all rulesets on a resolved spec."""

    def __init__(self):
        self.rulesets = [
            DesignRules(),
            SecurityRules(),
            PerformanceRules(),
        ]

    def audit(self, resolved_spec: dict) -> List[Issue]:
        """Run all rules and collect issues."""
        issues: List[Issue] = []
        for ruleset in self.rulesets:
            issues.extend(ruleset.check(resolved_spec))
        # Sort by severity then path
        severity_order = {'error': 0, 'warn': 1, 'info': 2}
        return sorted(issues, key=lambda i: (severity_order[i.severity], i.path))
