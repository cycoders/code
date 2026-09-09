import typer
from rich.console import Console

app = typer.Typer(help="SBOM diff and policy tool")
console = Console()

@app.command()
def diff(old: str, new: str, format: str = "table", fail_on: str = None):
    """Diff two SBOM files."""
    console.print(f"Diffing {old} vs {new} (format={format})")

@app.command()
def policy_check(sbom: str, rules: str):
    """Evaluate SBOM against policy."""
    console.print(f"Checking {sbom} with {rules}")