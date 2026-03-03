import typer
from typing import List, Optional

from rich.console import Console

from .cors_tester import CorsTester
from .models import AuditConfig, AuditReport
from .output import render_console, render_json

app = typer.Typer(no_args_is_help=True)
console = Console()

@app.command(name="test")
def test_command(
    url: str = typer.Argument(..., help="Target API endpoint URL"),
    origins: List[str] = typer.Option(
        ["http://localhost:3000"], "--origin/-o", help="Test origins"
    ),
    methods: List[str] = typer.Option(
        ["GET", "POST"], "--method/-m", help="Methods for preflight"
    ),
    request_headers: List[str] = typer.Option(
        [], "--request-header/-H", help="Custom headers for preflight (e.g., x-custom)"
    ),
    credentials: bool = typer.Option(False, "--credentials/-c"),
    timeout: float = typer.Option(10.0, "--timeout"),
    output: str = typer.Option("console", "--output/-O", help="console|json"),
):
    """Audit CORS configuration for the given URL."""

    config = AuditConfig(
        url=url,
        origins=origins,
        methods=methods,
        request_headers=request_headers,
        credentials=credentials,
        timeout=timeout,
    )

    try:
        tester = CorsTester(config)
        report = tester.run()
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(code=1)

    if output == "json":
        render_json(report)
    else:
        render_console(report)

if __name__ == "__main__":
    app()