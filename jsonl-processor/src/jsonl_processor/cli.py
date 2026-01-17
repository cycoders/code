import sys
import typer
from typing import Optional
from rich.traceback import install

install(show_locals=False)

from .processor import (
    run_filter,
    run_transform,
    run_sample,
    run_aggregate,
    run_stats,
)
from .utils import parse_value

app = typer.Typer(add_completion=False, no_args_is_help=True)

@app.command(name="filter")
def filter_cmd(
    input_file: Optional[str] = typer.Argument(None, help="Input JSONL (default: stdin)"),
    output_file: Optional[str] = typer.Argument(None, help="Output JSONL (default: stdout)"),
    field: str = typer.Option(..., "--field", help="JMESPath field expr"),
    op: str = typer.Option("==", "--op", help="Operator: == != > < >= <= contains"),
    value: str = typer.Option(..., "--value", help="Value (auto-typed)"),
    verbose: bool = typer.Option(False, "--verbose/-v"),
    strict: bool = typer.Option(False, "--strict"),
):
    """Filter records matching field OP value."""
    parsed_value = parse_value(value)
    run_filter(input_file, output_file, field, op, parsed_value, strict, verbose)

@app.command()
def transform(
    input_file: Optional[str] = typer.Argument(None),
    output_file: Optional[str] = typer.Argument(None),
    expr: str = typer.Option(..., "--expr", help="JMESPath expr to project/transform"),
    verbose: bool = typer.Option(False, "--verbose/-v"),
    strict: bool = typer.Option(False, "--strict"),
):
    """Transform records with JMESPath expr."""
    from .processor import run_transform
    run_transform(input_file, output_file, expr, strict, verbose)

@app.command()
def sample(
    input_file: Optional[str] = typer.Argument(None),
    output_file: Optional[str] = typer.Argument(None),
    fraction: float = typer.Option(0.1, "--fraction/-f", min=0.0, max=1.0),
    seed: Optional[int] = typer.Option(None, "--seed"),
    verbose: bool = typer.Option(False, "--verbose/-v"),
    strict: bool = typer.Option(False, "--strict"),
):
    """Random subsample (Bernoulli)."""
    from .processor import run_sample
    if seed is not None:
        import random
        random.seed(seed)
    run_sample(input_file, output_file, fraction, strict, verbose)

@app.command()
def aggregate(
    input_file: Optional[str] = typer.Argument(None),
    output_file: Optional[str] = typer.Argument(None),
    group_by: str = typer.Option(..., "--group-by"),
    metrics: str = typer.Option("count", "--metrics", help="e.g. count,sum:revenue,avg:price,min:price"),
    verbose: bool = typer.Option(False, "--verbose/-v"),
    strict: bool = typer.Option(False, "--strict"),
):
    """Aggregate by group."""
    from .processor import run_aggregate
    run_aggregate(input_file, output_file, group_by, metrics, strict, verbose)

@app.command()
def stats(
    input_file: Optional[str] = typer.Argument(None),
    metrics: str = typer.Option("count", "--metrics", help="count,unique:field,sum:amount,..."),
    verbose: bool = typer.Option(False, "--verbose/-v"),
    strict: bool = typer.Option(False, "--strict"),
):
    """Compute global stats (table output)."""
    from .processor import run_stats
    run_stats(input_file, metrics, strict, verbose)

if __name__ == "__main__":
    app()