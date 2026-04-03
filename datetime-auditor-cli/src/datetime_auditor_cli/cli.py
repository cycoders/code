import typer
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn
import rich.progress

from .auditor import audit_directory
from .reporter import report


app = typer.Typer(add_completion=False)

@app.command()
def audit(
    path: Path = typer.Argument(Path("."), help="Directory to audit"),
    fmt: str = typer.Option("table", "--format/-f", help="Output: table|json|html"),
):
    """
    Audit Python files for datetime/timezone issues.
    """
    if not path.is_dir():
        typer.echo("[red]Error:[/] Path must be a directory.", err=True)
        raise typer.Exit(code=1)

    console = typer.console
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Auditing Python files...", total=None)
        issues = audit_directory(path)
        progress.remove_task(task)

    report(issues, fmt, console)


if __name__ == "__main__":
    app()