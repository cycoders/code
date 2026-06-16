from dataclasses import dataclass
from typing import Any

@dataclass
class PlanDiff:
    cost_delta: float
    node_changes: list[str]

def diff_plans(base: str, head: str, query_file: str | None) -> PlanDiff:
    """Core diff logic (stubbed for skeleton)."""
    return PlanDiff(cost_delta=0.0, node_changes=[])