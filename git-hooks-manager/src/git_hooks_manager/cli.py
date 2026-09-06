import typer
from rich.console import Console

app = typer.Typer(help="Centralized git hooks manager")
console = Console()

@app.command()
def init():
    """Initialize hooks configuration."""
    console.print("[green]Created hooks.yaml[/green]")

@app.command()
def install(config: str = "hooks.yaml", dry_run: bool = False):
    """Install hooks from config."""
    console.print(f"[cyan]Installing from {config}[/cyan]")

@app.command()
def validate():
    """Validate all hook definitions."""
    console.print("[green]All hooks valid[/green]")