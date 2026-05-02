import typer

from rich.console import Console

from . import __version__

from .identifier import identify, format_results

from .hashes import HASHES_BY_HEX_LEN


app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command()
def identify_cmd(
    hash_input: str,
    all_candidates: bool = typer.Option(False, "--all", help="Show all candidates"),
    batch: str = typer.Option(None, "--batch", help="Batch file (one hash per line)"),
):
    """
    Identify hash algorithm(s) from a hex digest.
    """
    if batch:
        _handle_batch(batch)
    else:
        results = identify(hash_input, all_candidates)
        if len(results) == 1 and not all_candidates:
            console.print(f"[bold green]{results[0]['name']}[/bold green]")
        else:
            format_results(results, hash_input)


@app.command()
def list_candidates(hexlen: int):
    """
    List all candidates for a given hex length.
    """
    candidates = HASHES_BY_HEX_LEN.get(hexlen, [])
    if not candidates:
        console.print(f"[yellow]No hashes known for hex length {hexlen}.[/yellow]")
        return
    results = sorted(candidates, key=lambda h: h["priority"], reverse=True)
    format_results(results, f"len={hexlen}")


@app.command()
def version():
    console.print(f"hash-identifier-cli [bold cyan]v{__version__}[/bold cyan]")


def _handle_batch(file_path: str):
    from rich.progress import Progress, SpinnerColumn, TextColumn

    results = []
    with open(file_path) as f, Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
    ) as progress:
        task = progress.add_task("Processing hashes...", total=None)
        for line_num, line in enumerate(f, 1):
            h = line.strip()
            if h:
                try:
                    res = identify(h, False)
                    status = res[0]["name"] if res else "Unknown"
                except ValueError:
                    status = "Invalid"
                results.append({"hash": h[:16] + "...", "status": status})
            progress.advance(task)

    # Summary table
    from rich.table import Table
    table = Table(title="Batch Results")
    table.add_column("Hash (truncated)", style="dim")
    table.add_column("Identified As", style="green")
    for r in results:
        table.add_row(r["hash"], r["status'])
    console.print(table)


if __name__ == "__main__":
    app()

__all__ = ["app"]