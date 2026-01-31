import typer
from rich.traceback import install
from rich_click import RichClick

from .auditor import Auditor
from .scanner import WebScanner
from .csp_generator import CSPGenerator
from . import __version__


install(show_locals=True)
app = typer.Typer(no_args_is_help=True)


@app.command()
def audit(
    url: str = typer.Argument(..., help="Target URL"),
    output_json: bool = typer.Option(False, "--json", help="JSON output"),
    timeout: int = typer.Option(10, "--timeout", help="Request timeout (s)"),
    user_agent: str = typer.Option(None, "--user-agent", help="Custom User-Agent"),
) -> None:
    """Audit security headers with scoring."""
    try:
        auditor = Auditor(timeout=timeout, user_agent=user_agent)
        auditor.audit(url, output_json)
    except Exception as e:
        typer.echo(f"[red]Error:[/] {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def generate(
    url: str = typer.Argument(..., help="Target URL"),
    output: str = typer.Option(None, "--output/-o", help="Save policy to file"),
    timeout: int = typer.Option(10, "--timeout"),
    user_agent: str = typer.Option(None, "--user-agent"),
) -> None:
    """Generate CSP policy from site content."""
    try:
        scanner = WebScanner(timeout=timeout, user_agent=user_agent)
        data = scanner.scan(url, fetch_html=True)
        generator = CSPGenerator()
        policy = generator.generate(data["html"], data["url"])

        from rich.panel import Panel
from rich.console import Console
        console = Console()

        if output:
            with open(output, "w") as f:
                f.write(policy + "\n")
            console.print(f"[green]✅ CSP saved to [italic]{output}[/]"])
        else:
            console.print(Panel(policy, title="[bold blue]Generated CSP[/bold blue]", expand=False))
    except Exception as e:
        typer.echo(f"[red]Error:[/] {e}", err=True)
        raise typer.Exit(code=1)


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", help="Show version"),
) -> None:
    if version:
        typer.echo(f"security-headers-auditor {__version__}")
        raise typer.Exit()


if __name__ == "__main__":
    app(prog_name="security-headers-auditor")
