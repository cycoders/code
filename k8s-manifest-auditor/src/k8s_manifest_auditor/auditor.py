import logging
from pathlib import Path
from typing import List

from .parser import parse_manifests
from .rules import get_all_rules, Rule
from .types import Issue

logger = logging.getLogger(__name__)


def audit_path(root_path: Path, severity_filter: str = "ALL") -> List[Issue]:
    """
    Audit all manifests in path.

    :param root_path: Directory to scan
    :param severity_filter: Filter issues (ALL, HIGH, MEDIUM, LOW)
    :return: Filtered issues
    """
    manifests = parse_manifests(root_path)
    all_issues = []

    for manifest in manifests:
        kind = manifest.get("kind", "Unknown")
        metadata = manifest.get("metadata", {})
        namespace = metadata.get("namespace", "default")
        name = metadata.get("name", "unknown")
        resource_id = f"{kind}/{namespace}/{name}"

        for rule in get_all_rules():
            issues = rule(manifest, resource_id)
            all_issues.extend(issues)

    # Filter
    severity_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    filtered = [
        i for i in all_issues
        if severity_filter == "ALL" or i.severity == severity_filter
    ]
    filtered.sort(key=lambda i: (-severity_order.get(i.severity, 0), i.resource))

    logger.info(f"Found {len(filtered)} issues in {len(manifests)} manifests")
    return filtered
