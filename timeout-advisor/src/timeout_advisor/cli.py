import typer
from rich.console import Console
from .analyzer import recommend_timeouts

app = typer.Typer(help="Recommend production-grade timeouts from latency data")
console = Console()

@app.command()
def main(input: str = typer.Option("prometheus", help="prometheus|otlp|csv"), metric: str = "http_request_duration_seconds", p99_margin: float = 0.15):
    result = recommend_timeouts(input, metric, p99_margin)
    console.print(result)