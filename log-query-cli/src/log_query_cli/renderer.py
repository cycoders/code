import polars as pl
from rich.console import Console
from rich.table import Table
from rich import box
import sys

console = Console()


def render_df(df: pl.DataFrame, fmt: str) -> None:
    """Render Polars DF in specified format."""
    if fmt == "table":
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        for col in df.columns:
            table.add_column(col.title(), style="cyan", no_wrap=True)
        for row in df.rows():
            table.add_row(*[str(x) or "" for x in row])
        console.print(table)
    elif fmt == "json":
        print(df.write_json(row_oriented=True, indent=2))
    elif fmt == "csv":
        print(df.write_csv())
    elif fmt == "chart":
        if df.height == 0:
            console.print("No data for chart.")
            return
        # Assume first col for grouping, make bar chart
        group_col = df.columns[0]
        metric_col = "cnt" if "cnt" in df.columns else df.columns[-1]
        if metric_col not in df.columns:
            console.print("Chart needs 'cnt' or numeric col.")
            return
        counts = df.with_columns(pl.col(metric_col).sum().alias("total")).select(group_col, metric_col)
        max_val = counts[metric_col].max()
        bar_width = 50
        for row in counts.sort(metric_col, descending=True).iter_rows(named=True):
            val = row[metric_col]
            bar_len = int((val / max_val) * bar_width) if max_val > 0 else 0
            bar = "█" * bar_len + "░" * (bar_width - bar_len)
            console.print(f"{row[group_col]:<20} |{bar}| {val:>8,.0f}")
    else:
        print(df)

    if df.height > 0:
        console.print(f"\n[bold green]{df.height}[/] rows", style="dim")
