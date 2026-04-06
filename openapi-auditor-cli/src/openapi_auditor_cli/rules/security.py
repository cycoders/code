from typing import List, Dict, Any

from ..models import Issue
from .base import Rule


class SecurityRules(Rule):
    """Security-focused rules."""

    rule_id = "security"

    def check(self, spec: Dict[str, Any]) -> List[Issue]:
        issues = []
        components = spec.get("components", {})
        sec_schemes = components.get("securitySchemes", {})
        if not sec_schemes and any(spec.get("security")):
            issues.append(Issue(
                ["components", "securitySchemes"],
                "security.no-schemes",
                "Security referenced but no schemes defined",
                "error",
                "Define schemes in components.securitySchemes."
            ))
        paths = spec.get("paths", {})
        for path, path_item in paths.items():
            if isinstance(path_item, dict):
                for method in ["post", "put", "patch", "delete"]:
                    op = path_item.get(method)
                    if isinstance(op, dict) and not op.get("security") and sec_schemes:
                        op_path = ["paths", path, method, "security"]
                        issues.append(Issue(
                            op_path,
                            "security.missing-auth",
                            "Mutation lacks security",
                            "warn",
                            "Add security requirements for data changes."
                        ))
        return issues
