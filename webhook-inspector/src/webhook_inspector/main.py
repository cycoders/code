import typer
from pathlib import Path
import signal
import sys
from contextlib import contextmanager

import rich.console

from .app import create_app
from .storage import Storage
from .config import load_config

cli = typer.Typer()
console = rich.console.Console()

@cli.command()
def main(
    port: int = typer.Option(8080, "--port", "-p", help="Port to listen on"),
    config: Path = typer.Option(None, "--config", "-c", help="Config YAML path"),
    dev: bool = typer.Option(False, "--dev", help="Development mode (reload)"),
):
    """Run the webhook inspector server."""
    cfg = load_config(config)

    storage = Storage(cfg.storage_dir)

    app = create_app(cfg, storage)

    @contextmanager
def server_lifecycle():
        console.print("[bold green]🚀 Starting Webhook Inspector on http://localhost:{port}/")
        console.print("📊 Dashboard: http://localhost:{port}/")
        console.print("[bold yellow]Press Ctrl+C to stop.")
        try:
            yield
        finally:
            stats = storage.stats()
            console.print(f"\n📈 Final stats: {stats['total']} requests, {stats['verified']} verified")

    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info" if not dev else "debug",
        reload=dev,
        access_log=False,
    )


@cli.command()
def list():
    """List captured webhooks."""
    # Placeholder for full impl, demo
    console.print("[TODO] List command")


@cli.command()
def replay(id: str, url: str):
    """Replay a webhook by ID to a URL."""
    console.print(f"[TODO] Replay {id} to {url}")


if __name__ == "__main__":
    cli()
