import typer
from rich.console import Console
from .profiler import profile_startup

app = typer.Typer(help="Profile CLI startup latency")
console = Console()

@app.command()
def main(
    target: str = typer.Argument(..., help="Command to profile"),
    runs: int = typer.Option(3, help="Number of runs for statistics"),
    fmt: str = typer.Option("text", help="Output format: text|json|md"),
):
    result = profile_startup(target, runs)
    if fmt == "json":
        console.print(result.json())
    else:
        console.print(result.render(fmt))