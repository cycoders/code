import typer
from rich.console import Console
from .engine import RaftEngine

app = typer.Typer()
console = Console()

@app.command()
def run(nodes: int = 5, steps: int = 20):
    """Run a simulation."""
    engine = RaftEngine(nodes)
    for _ in range(steps):
        engine.step()
    console.print(engine.nodes)

@app.command()
def replay(scenario: str):
    """Replay a saved scenario."""
    console.print(f"Replaying {scenario}")