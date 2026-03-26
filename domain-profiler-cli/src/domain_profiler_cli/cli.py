import typer
import json
import tomllib
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from .profilers import profile_domain

app = typer.Typer()
console = Console()

CONFIG_PATH = Path.home() / ".domain-profiler-cli" / "config.toml"
CACHE_DIR = Path.home() / ".cache" / "domain-profiler-cli"

@app.command()
def main(
    domain: str,
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
    no_dns: bool = typer.Option(False, "--no-dns"),
    no_whois: bool = typer.Option(False, "--no-whois"),
    no_ssl: bool = typer.Option(False, "--no-ssl"),
    no_headers: bool = typer.Option(False, "--no-headers"),
    no_tech: bool = typer.Option(False, "--no-tech"),
    no_security: bool = typer.Option(False, "--no-security"),
    port: int = typer.Option(443, "--port"),
    http: bool = typer.Option(False, "--http", help="Use HTTP"),
    timeout: float = typer.Option(10.0, "--timeout"),
    no_cache: bool = typer.Option(False, "--no-cache"),
):
    """Profile a domain comprehensively."""
    config = load_config(timeout)

    cache_key = CACHE_DIR / f"{domain.replace('.', '_')}.json"
    if not no_cache and cache_key.exists():
        import time
        if time.time() - cache_key.stat().st_mtime < config["cache_ttl_hours"] * 3600:
            console.print("[yellow]Using cache...[/]")
            result = json.loads(cache_key.read_text())
            if json_output:
                print(json.dumps(result, indent=2))
                return
            print_report(result)
            return

    with Progress(SpinnerColumn(), TextColumn("Profiling {task.description}"), console=console) as progress:
        task = progress.add_task("Domain", total=None)
        result = profile_domain(
            domain,
            include_dns=not no_dns,
            include_whois=not no_whois,
            include_ssl=not no_ssl,
            include_headers=not no_headers,
            include_tech=not no_tech,
            include_security=not no_security,
            port=port,
            use_http=http,
            timeout=timeout,
        )
        progress.update(task, completed=1)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_key.write_text(json.dumps(result))

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)

def load_config(default_timeout: float) -> Dict[str, Any]:
    config = {
        "timeout": default_timeout,
        "user_agent": "DomainProfiler/0.1.0",
        "cache_ttl_hours": 1,
    }
    CONFIG_PATH.parent.mkdir(exist_ok=True)
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "rb") as f:
            data = tomllib.load(f)
            config.update(data.get("core", {}))
    return config

def print_report(result: Dict[str, Any]):
    console.print(Panel(f"[bold cyan]Domain Profile: {result['domain']}[/]", box=box.ROUNDED))

    for section, data in result.items():
        if section == "domain":
            continue
        if not data or "error" in data:
            console.print(f"[red]{section.title()}: {data.get('error', 'Skipped')}[/]")
            continue

        table = Table(title=section.replace("_", " ").title(), box=box.ROUNDED)
        if section == "dns":
            table.add_column("Type")
            table.add_column("Records")
            for typ, recs in data.items():
                table.add_row(typ, ", ".join(recs[:5]) + ("..." if len(recs) > 5 else ""))
        elif section == "headers":
            table.add_column("Header")
            table.add_column("Value")
            for k, v in sorted(data.items()):
                table.add_row(k, str(v)[:100])
        elif section == "tech":
            table.add_column("Technology")
            table.add_column("Confidence")
            for t in data:
                table.add_row(t["name"], t["confidence"])
        elif section == "security":
            table.add_column("Metric")
            table.add_column("Value")
            table.add_row("Score", f"{data['score']}/100")
            for issue in data["issues"]:
                table.add_row("Issue", f"[red]{issue}[/]")
        else:
            table.add_column("Key")
            table.add_column("Value")
            for k, v in data.items():
                table.add_row(str(k), str(v))
        console.print(table)

if __name__ == "__main__":
    app()