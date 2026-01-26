from collections import defaultdict, Counter
from typing import Dict, Any

from terraform_plan_analyzer.parser import get_action


def summarize_changes(changes: list[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate changes by action and resource type."""
    action_counter = Counter()
    type_counter = defaultdict(Counter)

    for change in changes:
        action = get_action(change)
        action_counter[action] += 1
        resource_type = change["type"]
        type_counter[resource_type][action] += 1

    return {
        "action_totals": dict(action_counter),
        "type_details": {k: dict(v) for k, v in type_counter.items()},
        "total_changes": len(changes),
    }


def format_summary(summary: Dict[str, Any]) -> str:
    """Format summary as readable text."""
    lines = ["## Change Summary"]
    for action, count in sorted(summary["action_totals"].items()):
        lines.append(f"  {action.upper()}: {count}")
    lines.append("")
    lines.append("## By Resource Type")
    for rtype, actions in sorted(summary["type_details"].items()):
        lines.append(f"  {rtype}: {actions}")
    return "\n".join(lines)