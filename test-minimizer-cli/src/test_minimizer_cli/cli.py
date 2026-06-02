import typer
from rich.console import Console
from test_minimizer_cli.minimizer import DeltaMinimizer

app = typer.Typer(help="Delta-debugging test minimizer")
console = Console()

@app.command()
def minimize(test_path: str, granularity: int = 2):
    """Minimize a failing test case."""
    console.print(f"[bold]Minimizing[/] {test_path}")
    # placeholder execution hook
    def always_fail(p): return True
    minimizer = DeltaMinimizer(always_fail, granularity)
    result = minimizer.minimize(open(test_path).read())
    console.print(result)