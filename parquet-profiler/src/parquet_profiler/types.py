from dataclasses import dataclass, asdict
from typing import List, Any, Optional, Dict
from enum import Enum

class OutputFormat(str, Enum):
    TABLE = "table"
    JSON = "json"

@dataclass
class ColumnStats:
    name: str
    pa_type: str
    logical_type: str
    count: int
    null_count: int
    null_pct: float
    min_val: Optional[Any] = None
    max_val: Optional[Any] = None
    mean: Optional[float] = None
    distinct_approx: Optional[int] = None
    top_values: Optional[Dict[str, int]] = None
    histogram_ascii: Optional[str] = None
    quality_alerts: List[str] = None

    def to_dict(self):
        return asdict(self)

@dataclass
class SchemaInfo:
    fields: List[Dict[str, Any]]
    num_rows: int
    num_columns: int
    total_size_bytes: Optional[int]

@dataclass
class ProfileResult:
    path: str
    schema: SchemaInfo
    columns: List[ColumnStats]
    alerts: List[str]

    def __rich__(self):
        from rich.table import Table
        from rich.panel import Panel
        table = Table(title="Column Statistics")
        table.add_column("Name", style="cyan")
        table.add_column("Type")
        table.add_column("Count")
        table.add_column("Null%", justify="right")
        table.add_column("Min")
        table.add_column("Max")
        table.add_column("Mean")
        table.add_column("Distinct")
        for col in self.columns:
            top = ', '.join(f"{k}:{v}%" for k,v in list(col.top_values.items())[:3]) if col.top_values else ""
            table.add_row(
                col.name,
                f"{col.pa_type}/{col.logical_type}",
                str(col.count),
                f"{col.null_pct:.1%}",
                str(col.min_val) if col.min_val is not None else "",
                str(col.max_val) if col.max_val is not None else "",
                f"{col.mean:.2f}" if col.mean else "",
                str(col.distinct_approx) if col.distinct_approx else top,
            )
        yield table
        if self.alerts:
            yield Panel("\n".join(self.alerts), title="Quality Alerts", border_style="yellow")

@dataclass
class CompareResult:
    path1: str
    path2: str
    schema_diff: Dict[str, str]
    stats_diffs: List[Dict[str, Any]]
