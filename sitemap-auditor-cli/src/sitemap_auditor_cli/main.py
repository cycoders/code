import asyncio
import typer
from pathlib import Path
from typing import Optional
import rich.console

from .auditor import audit_sitemap
from .reporter import print_summary, print_table, report_to_file


app = typer.Typer(help="Sitemap Auditor CLI", add_completion=False)
console = rich.console.Console()


@app.command()
def audit(
    sitemap_url: str,
    concurrency: int = typer.Option(50, "--concurrency/-c", min=1, max=200, help="Max concurrent requests"),
    timeout: float = typer.Option(10.0, "--timeout/-t", help="Per-URL timeout (s)"),
    respect_robots: bool = typer.Option(True, "--respect-robots/--ignore-robots"),
    output: str = typer.Option("table", "--output/-o", help="table|summary|json|csv|html"),
    output_file: Optional[Path] = typer.Option(None, "--file/-f", help="Output file (auto-ext)"),
    user_agent: str = typer.Option(
        "SitemapAuditorCLI/0.1.0 (+https://github.com/cycoders/code/tree/main/sitemap-auditor-cli)",
        "--user-agent/-u",
    ),
    max_depth: int = typer.Option(3, "--max-depth", help="Max sitemap recursion depth"),
):
    """
    Audit sitemap: check reachability, redirects, performance, robots compliance.
    """
    async def run_audit():
        results = await audit_sitemap(
            sitemap_url,
            concurrency,
            timeout,
            respect_robots,
            max_depth,
            user_agent,
        )
        print_summary(results)

        if output_file:
            report_to_file(results, output, output_file)
            console.print(f"[green]✓ Report saved: {output_file}[/green]")
        elif output == "table":
            print_table(results)
        elif output == "summary":
            pass  # Summary already printed
        else:
            default_path = Path(f"audit_report.{output}")
            report_to_file(results, output, default_path)
            console.print(f"[green]✓ Report saved: {default_path}[/green]")

    try:
        asyncio.run(run_audit())
    except KeyboardInterrupt:
        console.print("\n[red]✗ Audit interrupted by user.[/red]")
    except Exception as e:
        typer.echo(f"[red]✗ Audit failed: {str(e)}[/red]", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()