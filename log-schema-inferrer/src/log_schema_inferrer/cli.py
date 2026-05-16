import typer
from rich.console import Console
from rich.progress import track

from .inferrer import infer_schema
from .generator import generate_parser

app = typer.Typer(help="Infer log schemas and generate parsers")
console = Console()

@app.command()
def infer(path: str, output: str = "parsers"):
    """Infer schema from log files and generate parser."""
    console.print(f"[bold]Analyzing[/bold] {path}...")
    schema = infer_schema(path)
    generate_parser(schema, output)
    console.print("[green]Parser generated successfully[/green]")

@app.command()
def generate(schema: str, lang: str = "python"):
    """Generate parser from existing schema file."""
    console.print(f"Generating {lang} parser from {schema}")