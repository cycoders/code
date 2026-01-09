from typing import List, Dict, Any, Optional
from .models import LicenseInfo

PERMISSIVE_LICENSES = {
    "MIT",
    "Apache-2.0",
    "BSD-3-Clause",
    "BSD-2-Clause",
    "ISC",
    "Unlicense",
    "0BSD",
}
COPYLEFT_LICENSES = {"GPL", "LGPL", "AGPL", "MPL"}


def classify_license(license_str: str) -> str:
    upper = license_str.upper()
    if any(p in upper for p in PERMISSIVE_LICENSES):
        return "permissive"
    if any(c in upper for c in COPYLEFT_LICENSES):
        return "copyleft"
    if any(word in upper for word in ("PROPRIETARY", "COMMERCIAL")):
        return "proprietary"
    return "unknown"


def apply_policy(
    deps: List[LicenseInfo], config: Dict[str, Any]
) -> List[LicenseInfo]:
    policy = config.get("policy", {})
    allowed = set(policy.get("allowed", []))
    risky_patterns = policy.get("risky", [])

    for dep in deps:
        dep.classification = classify_license(dep.license)
        is_permissive = dep.classification == "permissive"
        is_allowed = dep.license in allowed
        is_risky = any(pattern.replace("*", "(.*)") in dep.license for pattern in risky_patterns)
        dep.approved = is_permissive or is_allowed and not is_risky

    return deps
