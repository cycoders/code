import typer
from rich.console import Console
import sys

from .benchmarker import run_benchmark
from .reporter import print_results

app = typer.Typer(no_args_is_help=True)
console = Console(file=sys.stderr)

@app.command()
def main(
    url: str = typer.Argument(..., help="Target HTTPS URL"),
    runs: int = typer.Option(5, "--runs", min=1, max=50, help="Benchmark iterations"),
    http2: bool = typer.Option(True, "--http2", help="Include HTTP/2 baseline"),
    method: str = typer.Option("GET", "--method", help="HTTP method (GET/HEAD)"),
    max_body: int = typer.Option(1024 * 1024, "--max-body", help="Max response body (bytes)"),
    headers: list[str] = typer.Option([], "-H", help="Custom headers (repeatable)"),
    output: typer.Literal["table", "json", "csv"] = "table",
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose logging"),
) -> None:
    """Benchmark HTTP/3 (QUIC) vs HTTP/2 performance."""
    try:
        results = run_benchmark(url, runs, http2, method, max_body, headers, verbose)
        print_results(results, output)
    except ValueError as e:
        console.print(f"[red]Invalid input:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Benchmark failed:[/red] {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
