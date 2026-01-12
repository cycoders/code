import json
import typer
from pathlib import Path

from .checker import check_propagation
from .output import print_propagation_table, print_json, print_csv
from .resolvers import RESOLVERS


app = typer.Typer(help="DNS Propagation Monitor", pretty_exceptions_enable=False)


@app.command(name="check")
def check_command(
    domain: str = typer.Argument(..., help="Domain to check"),
    rdtype: str = typer.Option("A", "--type", "-t", help="Record type (A, AAAA, MX, etc.)"),
    expected: str = typer.Option(
        ..., "--expected", "-e", help="Expected exact response (e.g. '93.184.216.34')"
    ),
    timeout: float = typer.Option(
        5.0, "--timeout", "-T", min=0.1, max=30, help="Query timeout (s)"
    ),
    max_workers: int = typer.Option(20, "--workers", "-w", min=1, max=50),
    resolvers_file: Path = typer.Option(
        None,
        "--resolvers-file",
        "-r",
        help="Custom resolvers JSON file (overrides default)",
    ),
    json_out: bool = typer.Option(False, "--json", "-j", help="JSON output"),
    csv_out: bool = typer.Option(False, "--csv", "-c", help="CSV output"),
):
    """Check DNS propagation status."""
    console = typer.console
    console.print(
        f"[bold blue]Checking {domain} ({rdtype}) expecting [green]\'{expected}'[/][/bold blue]"
    )

    resolvers = RESOLVERS
    if resolvers_file:
        if not resolvers_file.exists():
            raise typer.BadParameter(f"Resolvers file not found: {resolvers_file}")
        resolvers = json.loads(resolvers_file.read_text())
        if not isinstance(resolvers, list):
            raise typer.BadParameter("Resolvers file must be JSON list")

    console.print("[bold yellow]Querying resolvers...[/]")

    try:
        results = check_propagation(
            domain, rdtype, expected, resolvers, timeout, max_workers
        )
    except ValueError as e:
        typer.echo(f"[red]Error: {e}[/red]", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"[red]Unexpected error: {e}[/red]", err=True)
        raise typer.Exit(1)

    if json_out:
        print_json(results)
    elif csv_out:
        print_csv(results)
    else:
        print_propagation_table(results)


if __name__ == "__main__":
    app()