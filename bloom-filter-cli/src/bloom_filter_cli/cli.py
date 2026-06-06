import typer
from rich.console import Console
from bloom_filter_cli import calculator, simulator

app = typer.Typer(help="Bloom filter sizing and simulation toolkit")
console = Console()

@app.command()
def size(elements: int, fp: float = 0.01):
    """Compute optimal m and k."""
    m, k = calculator.optimal_params(elements, fp)
    console.print(f"m={m} bits, k={k} hashes, fp≈{fp}")

@app.command()
def simulate(config: str):
    """Run Monte-Carlo simulation from YAML config."""
    console.print(simulator.run(config))