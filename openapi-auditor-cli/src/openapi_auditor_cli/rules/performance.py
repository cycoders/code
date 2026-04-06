from typing import List, Dict, Any

from ..models import Issue
from .base import Rule


class PerformanceRules(Rule):
    """Performance and scalability rules."""

    rule_id = "performance"

    def check(self, spec: Dict[str, Any]) -> List[Issue]:
        issues = []
        paths = spec.get("paths", {})
        for path, path_item in paths.items():
            if path.endswith("{proxy+}") or "{**}" in path:
                issues.append(Issue(
                    ["paths", path],
                    "performance.wildcard-path",
                    "Wildcard/catch-all path detected",
                    "warn",
                    "Prefer explicit paths for caching/routing."
                ))
            if isinstance(path_item, dict):
                for method, op in path_item.items():
                    if isinstance(op, dict):
                        responses = op.get("responses", {})
                        if len(responses) > 10:
                            issues.append(Issue(
                                ["paths", path, method, "responses"],
                                "performance.too-many-responses",
                                f"Too many response codes: {len(responses)}",
                                "info",
                                "Consolidate common cases (default)."
                            ))
                        schemas = op.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema", {})
                        if isinstance(schemas.get("enum"), list) and len(schemas["enum"]) > 20:
                            issues.append(Issue(
                                ["paths", path, method, "requestBody"],
                                "performance.large-enum",
                                "Large enum (>20 items)",
                                "warn",
                                "Use string patterns or sub-resources."
                            ))
        return issues
