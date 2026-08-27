import typer
from rich.console import Console
from rich import print

from .canonicalize import canonicalize, verify

app = typer.Typer(help="Canonical JSON toolkit (RFC 8785)")
console = Console()

@app.command()
def canon(input: str, output: str = typer.Option(None, "--out")):
    """Canonicalize JSON file or stdin."""
    import json, sys
    data = json.load(open(input) if input != "-" else sys.stdin)
    result = canonicalize(data)
    if output:
        open(output, "w").write(result)
    else:
        print(result)

@app.command()
def check(original: str, candidate: str):
    """Verify two JSON files have identical canonical form."""
    import json
    o = json.load(open(original))
    c = json.load(open(candidate))
    if verify(o, c):
        console.print("[green]identical[/green]")
    else:
        console.print("[red]different[/red]")
        raise typer.Exit(1)