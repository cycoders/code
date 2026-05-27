import typer
from rich import print
from rich.table import Table

app = typer.Typer(help="ULID toolkit")

@app.command()
def generate(count: int = 1, monotonic: bool = False):
    from .core import generate
    for _ in range(count):
        print(generate(monotonic))

@app.command()
def inspect(ulid: str):
    from .core import parse
    u = parse(ulid)
    print(f"Timestamp: {u.timestamp}")
    print(f"Randomness: {u.randomness.hex()}")