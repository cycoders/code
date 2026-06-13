import typer
from rich.console import Console
from .analyzer import ImpactAnalyzer

app = typer.Typer(help="Predict which tests are impacted by code changes")
console = Console()

@app.command()
def main(base_ref: str = "main", head_ref: str = "HEAD", coverage_file: str = ".coverage"):
    analyzer = ImpactAnalyzer(coverage_file)
    impacted = analyzer.analyze(base_ref, head_ref)
    console.print(impacted)