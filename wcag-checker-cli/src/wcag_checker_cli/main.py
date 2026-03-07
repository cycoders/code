import typer
import requests
from pathlib import Path
from rich import print as rprint
from .auditor import Auditor
from .reporter import console_report, json_report, html_report
from .types import Issue

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)


@app.command(name="scan")
def scan(
    input_: str = typer.Argument(..., help="URL or path to HTML file"),
    output: str = typer.Option("console", "--output", "-o", help="Output: console, json, html"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="TOML config file"),
    timeout: int = typer.Option(10, "--timeout", help="Request timeout (URL only)"),
):
    """Scan for WCAG 2.2 accessibility issues."""
    try:
        if input_.startswith(('http://', 'https://')):
            rprint("[blue]Fetching[/]", input_)
            resp = requests.get(
                input_,
                timeout=timeout,
                headers={'User-Agent': 'wcag-checker-cli/0.1.0'},
            )
            resp.raise_for_status()
            html = resp.text
        else:
            html = Path(input_).read_text(encoding='utf-8')

        auditor = Auditor(html, config=str(config) if config else None)
        rprint("[green]Parsing & auditing...[/]")
        auditor.audit()
        issues = auditor.issues_list
        score = auditor.get_score()

        if output == 'json':
            rprint(json_report(issues))
        elif output == 'html':
            report = html_report(issues)
            Path('wcag-report.html').write_text(report)
            rprint(f"[green]📄 Report saved: wcag-report.html (Score: {score})[/]")
        else:
            console_report(issues)
            rprint(f"\n[bold]Score: {score}[/] | Violations: {len(issues)}")

    except FileNotFoundError:
        typer.echo("❌ File not found.", err=True)
        raise typer.Exit(1)
    except requests.RequestException as e:
        typer.echo(f"❌ Fetch failed: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Audit failed: {e}", err=True)
        raise typer.Exit(1)


if __name__ == '__main__':
    app()
