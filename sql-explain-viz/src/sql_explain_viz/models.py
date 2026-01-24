from dataclasses import dataclass, field
from typing import Optional, List, Any


@dataclass
class PlanNode:
    node_type: str
    startup_cost: Optional[float] = None
    total_cost: Optional[float] = None
    plan_rows: Optional[int] = None
    plan_width: Optional[float] = None
    actual_total_time: Optional[float] = None
    actual_rows: Optional[int] = None
    actual_loops: Optional[int] = None
    extra: dict[str, Any] = field(default_factory=dict)
    children: List["PlanNode"] = field(default_factory=list)

    @property
    def label(self) -> str:
        parts = [self.node_type]
        if self.startup_cost is not None and self.total_cost is not None:
            parts.append(f"cost={self.startup_cost:.1f}..{self.total_cost:.1f}")
        if self.plan_rows is not None:
            parts.append(f"rows={self.plan_rows:,}")
        if self.actual_total_time is not None:
            parts.append(f"act.time={self.actual_total_time:.1f}ms")
        if self.actual_rows is not None:
            parts.append(f"a.rows={self.actual_rows:,}")
        return " | ".join(parts)