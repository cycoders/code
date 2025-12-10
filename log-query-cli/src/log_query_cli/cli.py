import typer
from pathlib import Path
import polars as pl
from tqdm import tqdm
import rich_click as click

click.rich_click.COMPLETE_KEYBINDING = "tab"

from .parser import parse_line
from .config import load_patterns
from .engine import run_query
from .renderer import render_df


app = typer.Typer(help="Blazing-fast log querying CLI.")


@app.command()
def query(
    sql: str = typer.Argument(..., help="SQL query (uses 'logs' table)"),
    files: list[Path] = typer.Argument(..., help="Log file(s)"),
    config: Path = typer.Option(None, "--config", help="YAML config for custom patterns"),
    fmt: str = typer.Option("table", "--format", help="Output: table, json, csv, chart"),
    limit: int = typer.Option(None, "--limit", help="Limit rows (post-query)"),
) -> None:
    """Query log files with SQL."""
    patterns = load_patterns(config)

    all_rows = []
    total_files = len(files)

    with tqdm(files, desc="Parsing files", unit="file") as pbar:
        for file_path in pbar:
            if not file_path.exists():
                typer.echo(f"❌ File not found: {file_path}", err=True)
                continue
            rows = []
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        parsed = parse_line(line, patterns)
                        if parsed:
                            rows.append(parsed)
                file_df = pl.DataFrame(rows)
                all_rows.extend(rows)  # For concat
                pbar.set_postfix(parsed=len(rows))
            except Exception as e:
                typer.echo(f"⚠️  Error parsing {file_path}: {e}", err=True)

    if not all_rows:
        typer.echo("No logs parsed.", err=True)
        raise typer.Exit(1)

    df = pl.DataFrame(all_rows)
    typer.echo(f"✅ Parsed {len(df):,} log entries", fg="green")

    try:
        result = run_query(df, sql)
        if limit:
            result = result.head(limit)
        render_df(result, fmt)
    except Exception as e:
        typer.echo(f"❌ Query error: {e}", err=True)
        typer.echo("Hint: Ensure SQL uses 'logs' table, columns match parsed fields.", err=True)
        raise typer.Exit(1)