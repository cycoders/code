import typer
import ast
from pathlib import Path
from .analyzer import DeadlockAnalyzer
from .reporter import report

app = typer.Typer(help="Static deadlock detector for Python")

@app.command()
def main(path: Path = typer.Argument(..., exists=True, file_okay=False)):
    """Analyze Python package for potential deadlocks."""
    analyzer = DeadlockAnalyzer()
    for py in path.rglob("*.py"):
        tree = ast.parse(py.read_text())
        result = analyzer.analyze(tree)
        report(result)

if __name__ == "__main__":
    app()