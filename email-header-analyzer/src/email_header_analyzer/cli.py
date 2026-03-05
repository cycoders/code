import sys
import typer
from typing import BinaryIO
from rich.console import Console
from rich.traceback import install

install(show_locals=True)

app = typer.Typer(
    name="email-header-analyzer",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    rich_markup_mode="rich",
)
console = Console(file=sys.stderr)

@app.command(help="Analyze email headers for deliverability issues.")
def analyze(
    eml: str = typer.Argument("-", help="EML file or '-' for stdin"),
    json: bool = typer.Option(False, "--json", help="Output JSON."),
    verbose: bool = typer.Option(False, "--verbose/-v", help="Verbose details."),
) -> None:
    """Analyze EML for auth/deliverability."""
    from .parser import parse_email_file_or_stdin
    from .auth_checker import AuthChecker
    from .reporter import generate_report

    try:
        msg, raw = parse_email_file_or_stdin(eml)
    except Exception as e:
        typer.echo(f"❌ Parse error: {e}", err=True)
        raise typer.Exit(1)

    checker = AuthChecker(msg, raw)
    analysis = checker.run_checks(verbose)

    if json:
        import json
        typer.echo(json.dumps(analysis, indent=2))
    else:
        generate_report(console, analysis, verbose)

if __name__ == "__main__":
    app()