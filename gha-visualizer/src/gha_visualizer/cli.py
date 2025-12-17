import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import box

from .parser import parse_workflow, extract_jobs
from .mermaid_renderer import generate_mermaid
from .analyzer import analyze


app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
console = Console()


@app.command(name="render")
def render_cmd(
    workflow_path: Path = typer.Argument(..., help="Path to GHA workflow YAML file"),
    output: Path = typer.Option("workflow.mmd", "--output", "-o", help="Output Mermaid file"),
):
    """Render Mermaid diagram from workflow YAML."""

    if not workflow_path.is_file():
        typer.echo(f"❌ Error: '{workflow_path}' is not a file.", err=True)
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("Parsing workflow..."),
        console=console,
    ) as progress:
        task = progress.add_task("", total=None)
        data = parse_workflow(workflow_path)
        jobs = extract_jobs(data)
        progress.remove_task(task)

    mermaid = generate_mermaid(jobs)
    output.write_text(mermaid, encoding="utf-8")

    console.print(f"✅ Mermaid diagram saved to [bold cyan]{output}[/bold cyan]")
    console.print("📱 Open at [bold blue]mermaid.live[/bold blue] to interact/export!")


@app.command()
def analyze_cmd(workflow_path: Path = typer.Argument(..., help="Path to GHA workflow YAML file")):
    """Generate analytics report for workflow."""

    if not workflow_path.is_file():
        typer.echo(f"❌ Error: '{workflow_path}' is not a file.", err=True)
        raise typer.Exit(1)

    with Progress(SpinnerColumn(), TextColumn("Analyzing..."), console=console) as progress:
        task = progress.add_task("", total=None)
        data = parse_workflow(workflow_path)
        jobs = extract_jobs(data)
        stats = analyze(jobs)
        progress.remove_task(task)

    table = Table(
        title="[bold cyan]GHA Workflow Analysis[/bold cyan]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("Number of Jobs", str(stats["jobs"]))
    table.add_row("Total Steps", str(stats["steps"]))
    table.add_row("Max Dependencies (out)", str(stats["max_outdegree"]))
    table.add_row("Max Indegree", str(stats["max_indegree"]))
    table.add_row("Parallelism Estimate", str(stats["parallelism_estimate"]))

    console.print(table)

    if stats["issues"]:
        issues_table = Table(
            "Potential Issues",
            box=box.MINIMAL_HEAVY,
            show_header=True,
            header_style="bold red",
            title="⚠️  Warnings",
        )
        for issue in stats["issues"]:
            issues_table.add_row(issue)
        console.print(issues_table)
    else:
        console.print("✅ [green]No issues detected![/green]")


if __name__ == "__main__":
    app()