from typing import List, Dict, Any

from ..models import Issue
from .base import Rule


class DesignRules(Rule):
    """Design and usability rules."""

    rule_id = "design"

    def check(self, spec: Dict[str, Any]) -> List[Issue]:
        issues = []
        info = spec.get("info", {})
        if not info.get("title"):
            issues.append(Issue(
                ["info"],
                "design.missing-title",
                "Missing info.title",
                "error",
                "Every API spec needs a human-readable title."
            ))
        if not info.get("version"):
            issues.append(Issue(
                ["info"],
                "design.missing-version",
                "Missing info.version",
                "warn",
                "Specify semantic version for evolution tracking."
            ))

        paths = spec.get("paths", {})
        for path, path_item in paths.items():
            if isinstance(path_item, dict):
                for method, op in path_item.items():
                    if isinstance(op, dict):
                        op_path = ["paths", path, method]
                        if not op.get("summary"):
                            issues.append(Issue(
                                op_path + ["summary"],
                                "design.missing-summary",
                                "Operation missing summary",
                                "warn",
                                "Add a one-line summary for docs/tools."
                            ))
                        if not op.get("tags"):
                            issues.append(Issue(
                                op_path + ["tags"],
                                "design.missing-tags",
                                "Operation missing tags",
                                "warn",
                                "Use tags for grouping (e.g., 'users')."
                            ))
                        params = op.get("parameters", [])
                        if len(params) > 5:
                            issues.append(Issue(
                                op_path + ["parameters"],
                                "design.too-many-params",
                                f"Too many parameters: {len(params)}",
                                "warn",
                                "Consider query objects or pagination."
                            ))
        return issues
