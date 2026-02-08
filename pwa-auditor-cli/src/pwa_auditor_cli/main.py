import typer
from rich.console import Console
from rich.traceback import install

from .auditor import PWAAuditor
from .output import print_results


install(show_locals=True)  # Rich tracebacks

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
console = Console()


@app.command(help="Audit a URL for PWA compliance")
def audit(
    url: str = typer.Argument(..., help="URL to audit"),
    timeout: float = typer.Option(10.0, "--timeout", min=1.0, help="Request timeout (s)"),
    json: bool = typer.Option(False, "--json", help="JSON output for CI"),
) -> None:
    """Audit website for PWA compliance and print score/checklist."""
    try:
        auditor = PWAAuditor(url, timeout)
        results = auditor.run_checks()
        print_results(results, console, json)
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()

audit_app = app
