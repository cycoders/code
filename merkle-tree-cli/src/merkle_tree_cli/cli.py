import typer
from rich.console import Console

app = typer.Typer(help="Merkle tree builder and verifier")
console = Console()

@app.command()
def build(path: str):
    console.print(f"Building tree for {path}")

@app.command()
def prove(tree: str, index: int):
    console.print(f"Proof for index {index}")

if __name__ == "__main__":
    app()