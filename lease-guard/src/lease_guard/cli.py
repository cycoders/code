import typer
from rich import print
from .lease import LeaseClient

app = typer.Typer(help="lease-guard CLI")

@app.command()
def acquire(key: str, ttl: int = 30):
    client = LeaseClient()
    lease = client.acquire(key, ttl)
    print(f"[green]acquired[/green] {key} token={lease.token}")

@app.command()
def validate(key: str, token: str):
    print("validation not implemented in demo")