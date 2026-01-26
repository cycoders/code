from typing import List, Dict, Any
from rich.text import Text


RISK_RULES = [
    lambda c: "delete" in c["change"]["actions"] and ("prod" in c["address"].lower() or "production" in c["address"].lower()),
    lambda c: c["change"].get("after", {}).get("public_ip") is True,
    lambda c: c["type"].startswith("aws_iam") and "delete" in c["change"]["actions"],
    lambda c: c["type"] == "aws_s3_bucket" and c["change"].get("after", {}).get("acl") == "public-read",
    lambda c: "instance_type" in c["change"].get("after", {}) and "xlarge" in c["change"]["after"]["instance_type"],
    lambda c: len(c["change"].get("after", {})) > 50,  # Massive config change
    lambda c: "security_group" in c["type"] and "delete" in c["change"]["actions"],
    lambda c: "vpc" in c["address"].lower() and "public" in c["change"].get("after", {}, ""),
]

RISK_DESCS = [
    "Potential production data loss: deleting {address}",
    "Public exposure risk: enabling public_ip on {address}",
    "IAM disruption: modifying/deleting {address}",
    "S3 public access: setting ACL to public-read on {address}",
    "Cost spike: scaling to xlarge instance {address}",
    "Massive config change (>50 attrs): {address}",
    "Network security gap: deleting {address}",
    "Public VPC exposure: {address}",
]


def assess_risks(changes: List[Dict[str, Any]]) -> List[str]:
    """Apply heuristic rules to detect risks."""
    risks = []
    for change in changes:
        for idx, rule in enumerate(RISK_RULES):
            if rule(change):
                desc = RISK_DESCS[idx % len(RISK_DESCS)].format(address=change["address"])
                risks.append(f"🚨 {desc}")
                break  # One risk per change
    return risks


def format_risks(risks: List[str]) -> str:
    """Format risks as console-friendly output."""
    if not risks:
        return "✅ No risks."
    return "\n".join(risks)