from datetime import datetime
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, computed_field
from rich.table import Table


class Headers(BaseModel):
    """HTTP headers dict."""

    __root__: Dict[str, str]


class RateLimitInfo(BaseModel):
    """Parsed rate limit metadata."""

    limit: Optional[int] = None
    remaining: Optional[int] = None
    reset_timestamp: Optional[int] = None  # Unix seconds
    retry_after: Optional[Union[int, float]] = None
    window_seconds: Optional[int] = Field(None, description="Inferred window")
    headers_seen: List[str] = []

    @computed_field
    @property
    def reset_seconds(self) -> Optional[float]:
        if self.reset_timestamp:
            return max(0, self.reset_timestamp - datetime.now().timestamp())
        return None

    @computed_field
    @property
    def percentage_used(self) -> Optional[float]:
        if self.limit and self.remaining is not None:
            return ((self.limit - self.remaining) / self.limit) * 100
        return None

    def rich_table(self) -> Table:
        """Rich table representation."""
        table = Table(title="Rate Limit Status", box="heavy")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Limit", f"{self.limit or '?'} req")
        table.add_row("Remaining", f"{self.remaining or '?'} req")
        table.add_row("Used", f"{self.percentage_used:.1f}%" if self.percentage_used else "?")
        table.add_row("Reset", f"{self.reset_seconds:.0f}s" if self.reset_seconds else "?")
        table.add_row("Window", f"{self.window_seconds}s" if self.window_seconds else "?")
        return table


class TestStats(BaseModel):
    """Test results."""

    total_requests: int = 0
    successes: int = 0
    failures: int = 0
    avg_rps: float = 0.0
    peak_rps: float = 0.0
    burst_capacity: Optional[int] = None
    reset_time: Optional[float] = None

    def to_dict(self) -> Dict[str, float | int]:
        return self.model_dump()
