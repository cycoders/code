import asyncio
import json
import sys
import typer
from pathlib import Path
from typing import Optional

import yaml
from rich.console import Console
from rich.markup import escape

from reqbench import __version__
from reqbench.benchmarker import Benchmarker
from reqbench.models import BenchmarkConfig
from reqbench.reporter import print_table

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)
console = Console()

@app.command()
def version():
    """Show version."""
    console.print(f"ReqBench v{__version__}")

@app.command()
def bench(
    config_file: Optional[Path] = typer.Option(None, "-c", "--config", help="YAML config file"),
    url: Optional[str] = typer.Argument(None, help="Target URL"),
    method: str = typer.Option("GET", "-m", "--method"),
    headers: str = typer.Option("{}", "-H", "--headers", help="JSON dict str"),
    params: str = typer.Option("{}", "-p", "--params", help="JSON dict str"),
    json_data: str = typer.Option("null", "-j", "--json", help="JSON str"),
    data: str = typer.Option("null", "-d", "--data", help="JSON str"),
    clients: str = typer.Option("httpx,requests", "--clients", help="Comma-separated: httpx-sync,httpx,requests,aiohttp"),
    concurrency: int = typer.Option(10, "-C", "--concurrency", min=1, max=1000),
    duration: float = typer.Option(10.0, "-t", "--duration", min=1.0, max=300.0),
):
    """Benchmark HTTP requests across clients."""
    try:
        if config_file:
            if not config_file.exists():
                raise typer.BadParameter(f"Config file not found: {config_file}")
            with open(config_file) as f:
                data = yaml.safe_load(f)
            config = BenchmarkConfig.model_validate(data)
        else:
            if not url:
                raise typer.BadParameter("URL required unless --config used")
            config_dict = {
                "url": url,
                "method": method,
                "clients": [c.strip() for c in clients.split(",")],
                "concurrency": concurrency,
                "duration": duration,
            }
            # Parse JSON strings safely
            for field in ["headers", "params"]:
                val = locals()[field]
                if val != "{}":
                    config_dict[field] = json.loads(val)
            for field in ["json_data", "data"]:
                val = locals()[field]
                if val != "null":
                    config_dict[field.replace("_data", "")] = json.loads(val)
            config = BenchmarkConfig.model_validate(config_dict)

        typer.echo("Running benchmark...", nl=False)
        results = Benchmarker(config).run()
        print_table(results, config)
    except Exception as e:
        console.print(f"[red]Error:[/red] {escape(str(e))}")
        raise typer.Exit(1) from e

if __name__ == "__main__":
    app()