import sys
from pathlib import Path
from typing import List

import typer
from rich import print as rprint

from . import __version__
from .models import TestCase
from .output import print_summary, print_table, print_pytest_commands, output_json
from .parser import parse_junit_files
from .splitter import split_tests


app = typer.Typer(add_completion=False)
console = typer.core.Console(stderr=True)


@app.command(short_help="Split test suite into balanced CI jobs")
def split(
    input_paths: List[str] = typer.Argument(
        ...,
        help="JUnit XML file(s) or directory(ies)",
        metavar="[PATH ...]",
    ),
    jobs: int = typer.Option(
        4,
        "--jobs/-j",
        min=1,
        max=64,
        show_default=True,
        help="Number of parallel jobs/shards",
    ),
    output: str = typer.Option(
        "table",
        "--output/-o",
        show_choices=["table", "json", "pytest"],
        help="Output format",
    ),
    version: bool = typer.Option(False, "--version", help="Show version"),
) -> None:
    if version:
        rprint(f"test-suite-splitter {__version__}")
        raise typer.Exit()

    paths = [Path(p) for p in input_paths]
    tests = parse_junit_files(paths)

    if not tests:
        typer.echo("[red]No tests found in input paths.[/red]", err=True)
        raise typer.Exit(code=1)

    print_summary(tests, [])
    jobs_list = split_tests(tests, jobs)

    match output:
        case "table":
            print_table(jobs_list)
            print_pytest_commands(jobs_list)
        case "json":
            total_time = sum(t.duration for t in tests)
            typer.echo(output_json(jobs_list, len(tests), total_time))
        case "pytest":
            print_pytest_commands(jobs_list)
        case _:
            typer.echo(f"Unknown output: {output}", err=True)
            raise typer.Exit(code=1)


if __name__ == "__main__":
    app()