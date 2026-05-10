import sys
import typer
from pathlib import Path
from typing import Optional

import yaml
import rich_click as click

from .config import Config

from .scanner import scan_directory

from .reporter import Report


app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
console = typer.Console()


@app.command()
def scan(
    root: Path = typer.Argument(Path("."), help="Root directory to scan"),
    config_file: Path = typer.Option("ff-auditor.yaml", "--config", "-c", help="Config YAML"),
    active_file: Optional[Path] = typer.Option(None, "--active-flags", "-a", help="Active flags JSON/YAML"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file (md/json)"),
    fmt: str = typer.Option("console", "--format", "-f", help="Output format: console/md/json"),
):
    """Scan codebase for feature flag usages."""

    if not config_file.exists():
        typer.echo(f"Config not found: {config_file}", err=True)
        raise typer.Exit(1)

    try:
        with open(config_file, "r") as f:
            data = yaml.safe_load(f)
        config = Config.model_validate(data)
    except Exception as e:
        typer.echo(f"Invalid config: {e}", err=True)
        raise typer.Exit(1)

    usages = scan_directory(root, config)

    active_set: Optional[set[str]] = None
    if active_file and active_file.exists():
        with open(active_file, "r") as f:
            active_data = yaml.safe_load(f)
        active_set = set(active_data.get("flags", []))

    report = Report(usages, active_set)

    if fmt == "console" or not output:
        report.console_report(console)
    elif fmt == "md" and output:
        md = report.markdown_report()
        output.write_text(md)
        typer.echo(f"Report saved: {output}")
    elif fmt == "json" and output:
        js = report.json_report()
        output.write_text(yaml.safe_dump(js))
        typer.echo(f"JSON saved: {output}")
    else:
        typer.echo("Unsupported format/output combo", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
