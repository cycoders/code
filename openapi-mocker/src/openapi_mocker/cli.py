import logging
import sys
from pathlib import Path
from typing import List

import rich.traceback
import typer
from rich import box
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import track

from .server import create_mock_app


app = typer.Typer(no_args_is_help=True)
console = Console()

# Install rich traceback
rich.traceback.install(show_locals=True, console=console, width=console.width)


@app.command(help="Run mock server from OpenAPI spec")
def run(
    spec: Path = typer.Argument(..., exists=True, help="Path to OpenAPI 3.0 YAML/JSON spec"),
    host: str = typer.Option("127.0.0.1", "--host", help="Bind host"),
    port: int = typer.Option(8000, "--port", help="Bind port"),
    cors_origins: List[str] = typer.Option(
        [], "--cors-origins", help="CORS allowed origins (repeatable)"
    ),
):
    """
    Launch a mock API server from an OpenAPI spec.
    """
    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(console=console, rich_tracebacks=True),
            logging.StreamHandler(sys.stdout),
        ],
    )

    try:
        with console.status("[bold blue]Parsing OpenAPI spec..."):
            uvicorn_url = f"http://{host}:{port}"
            app_instance = create_mock_app(spec, cors_origins)

        console.print(
            Panel(
                f"[bold green]✓ Mock server ready![/bold green]\n"
                f"[blue]URL:[/blue] {uvicorn_url}\n"
                f"[blue]Spec:[/blue] {spec.name}\n"
                f"[yellow]Press Ctrl+C to stop.[/yellow]",
                title="[bold cyan]OpenAPI Mocker[/bold cyan]",
                border_style="cyan",
                box=box.ROUNDED,
            )
        )

        import uvicorn  # Delay import for faster CLI
        uvicorn.run(
            "openapi_mocker.server:create_mock_app",
            factory_kwargs={"spec_path": spec, "cors_origins": cors_origins},
            host=host,
            port=port,
            log_level="info",
            reload=False,
        )

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Shutdown requested...[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise
        sys.exit(1)