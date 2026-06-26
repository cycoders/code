import typer
from rich.console import Console

app = typer.Typer(help="Inspect live gRPC services via reflection")
console = Console()

@app.command()
def inspect(target: str):
    """Inspect a gRPC target."""
    console.print(f"Inspecting {target}")

@app.command()
def call(target: str, method: str):
    """Call a reflected method."""
    console.print(f"Calling {method} on {target}")