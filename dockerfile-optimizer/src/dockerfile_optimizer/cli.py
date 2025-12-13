import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .parser import parse_dockerfile
from .analyzer import analyze
from .suggester import suggest_optimized
from .renderer import render_mermaid


app = typer.Typer(help="Optimize Dockerfiles for smaller images & faster builds.")
console = Console()


@app.command(no_args_is_help=True)
def analyze(
    filepath: Path = typer.Argument(..., help="Path to Dockerfile"),
    output: Optional[Path] = typer.Option(None, "--output/-o", help="Save optimized DF"),
    mermaid: Optional[Path] = typer.Option(None, "--mermaid/-m", help="Save Mermaid graph"),
):
    """Analyze Dockerfile: issues, optimizations, Mermaid viz."""
    try:
        instructions = parse_dockerfile(str(filepath))
        if not instructions:
            typer.echo("No instructions found.", err=True)
            raise typer.Exit(1)

        analysis = analyze(instructions)

        # Summary
        summary_table = Table.grid(expand=True, padding=(0, 1))
        summary_table.add_row(
            "[bold]Layers[/bold]: [magenta]" + str(analysis["num_layers"]),
            "[bold]RUNs[/bold]: [magenta]" + str(analysis["num_runs"]),
            "[bold]Savings[/bold]: [green]~" + str(analysis["potential_savings_mb"]) + "MB",
        )
        console.print(Panel(summary_table, title="[bold green]Analysis Summary[/]"))

        # Issues
        if analysis["issues"]:
            issues_table = Table("Issue", expand=True, show_header=False, padding=(0, 1))
            for issue in analysis["issues"]:
                issues_table.add_row(issue)
            console.print(issues_table)
        else:
            console.print("[green bold]✓ No issues found![/]\n")

        # Optimized DF
        optimized_df = suggest_optimized(instructions)
        console.print(Panel(optimized_df, title="[bold blue]Suggested Optimized Dockerfile[/]"))

        # File outputs
        if mermaid:
            render_mermaid(instructions, str(mermaid))
            console.print(f"\n[green]📊 Mermaid graph → {mermaid}[/]" )
        if output:
            output.write_text(optimized_df)
            console.print(f"[green]💾 Optimized → {output}[/]" )

    except FileNotFoundError:
        typer.echo(f"❌ {filepath} not found", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
