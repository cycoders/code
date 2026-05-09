import typer
from pathlib import Path
from rich.console import Console
from rich.progress import track
from rich.table import Table
from rich import box

from .fuzzer import Fuzzer

app = typer.Typer(help="ReDoS Detector: Fuzzes regex for catastrophic backtracking.")
console = Console()

@app.command()
def check(
    regex: str = typer.Argument(..., help="Regex pattern to test"),
    timeout: float = typer.Option(0.1, "--timeout", min=0.01, help="Match timeout (s)"),
    max_gens: int = typer.Option(50, "--max-gens", min=10, help="Max generations"),
    pop_size: int = typer.Option(100, "--pop-size", min=20, help="Population size"),
):
    """Check a regex for ReDoS vulnerability."""
    try:
        fuzzer = Fuzzer(regex, timeout)
    except re.error as e:
        typer.echo(f"Invalid regex: {e}", err=True)
        raise typer.Exit(1)

    with console.status("[bold green]Fuzzing regex..."):
        result = fuzzer.fuzz(max_gens, pop_size)

    if result["vulnerable"]:
        console.print("[bold red]💥 Vulnerable![/bold red]")
        console.print(f"[yellow]Worst input:[/yellow] {repr(result['worst_input'][:80])}...")
        console.print(f"Length: [cyan]{len(result['worst_input']):,}[/cyan]")
        console.print(f"Time: [red]{result['max_time']:.3f}s[/red] (> [magenta]{timeout}s[/magenta] threshold)")
        console.print(f"Found in [green]{result['gens']}[/green] generations")
        raise typer.Exit(2)
    else:
        console.print("[bold green]✅ Safe[/bold green]")
        console.print(f"Max time: [green]{result['max_time']:.3f}s[/green] ({len(result['worst_input']):,} chars)")


@app.command()
def bench(timeout: float = typer.Option(0.1, "--timeout")):
    """Benchmark known vulnerable/safe regexes."""
    benchmarks = [
        (r"^(a+)+$", "Nested repeats"),
        (
            r"^([\\w\\!\\#$%&'*+\/=?`\{|}~^-]+(?:\\.[\\w\\!\\#$%&'*+\/=?`\{|}~^-]+)*)@((\\[[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\])|(([a-zA-Z\\-0-9]+\\.)+[a-zA-Z]{2,}))$",
            "Evil email",
        ),
        (r"^\\d{3}-\\d{2}-\\d{4}$", "SSN"),
        (r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", "Simple email"),
    ]

    table = Table(title="ReDoS Benchmarks", box=box.ROUNDED)
    table.add_column("Regex", style="cyan")
    table.add_column("Description")
    table.add_column("Status")
    table.add_column("Time (s)")
    table.add_column("Len")
    table.add_column("Gens")

    for regex, desc in track(benchmarks, description="Benchmarking..."):
        try:
            fuzzer = Fuzzer(regex, timeout)
            result = fuzzer.fuzz(30, 50)
            status = "[red]💥[/red]" if result["vulnerable"] else "[green]✅[/green]"
            table.add_row(
                regex[:40] + "..." if len(regex) > 40 else regex,
                desc,
                status,
                f"{result['max_time']:.2f}",
                f"{len(result['worst_input']):,}",
                str(result["gens"]),
            )
        except re.error:
            table.add_row(regex, desc, "[yellow]Invalid[/yellow]", "-", "-", "-")

    console.print(table)


if __name__ == "__main__":
    app()
