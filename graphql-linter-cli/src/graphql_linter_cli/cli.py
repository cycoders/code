import click
import sys
from pathlib import Path
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.progress import track

from graphql_linter_cli.schema_loader import load_schema
from graphql_linter_cli.auditor import Auditor
from graphql_linter_cli.reporter import Reporter

console = Console()

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option("0.1.0")
def cli():
    """GraphQL Linter CLI: Lint schemas for best practices."""
    pass


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option("--format", "output_format", type=click.Choice(["table", "json", "yaml"]), default="table")
@click.option("--max-errors", type=int, default=0, help="Fail if errors > N")
@click.option("--max-warnings", type=int, default=None, help="Fail if warnings > N")
@click.option("--ignore", multiple=True, help="Ignore specific rules")
@click.option("--verbose", is_flag=True, help="Verbose output")
def lint(paths: tuple[Path, ...], output_format: str, max_errors: int, max_warnings: int | None, ignore: tuple[str, ...], verbose: bool):
    """Lint GraphQL schema files/directories."""
    if not paths:
        click.echo("No paths provided.")
        sys.exit(1)

    all_issues = []
    schema_files = []

    for path in track(paths, description="Scanning paths"):
        if path.is_dir():
            schema_files.extend(path.rglob("*.graphql") | path.rglob("*.gql"))
        elif path.suffix in {"graphql", ".gql"}:
            schema_files.append(path)

    if verbose:
        click.echo(f"Found {len(schema_files)} schema files.")

    for schema_path in track(schema_files, description="Linting schemas"):
        try:
            schema = load_schema(schema_path)
            auditor = Auditor(schema, ignore_rules=set(ignore))
            issues = auditor.run()
            all_issues.extend(issues)
            if verbose:
                click.echo(f"{schema_path}: {len(issues)} issues")
        except Exception as e:
            console.print(f"[red]Failed to parse {schema_path}: {e}[/red]")
            all_issues.append({"path": str(schema_path), "severity": "error", "message": f"Parse error: {e}", "rule": "parse-error"})

    reporter = Reporter(all_issues)
    report = reporter.generate(output_format)

    if output_format == "table":
        console.print(report)
    else:
        click.echo(report)

    error_count = len([i for i in all_issues if i["severity"] == "error"])
    warn_count = len([i for i in all_issues if i["severity"] == "warning"])

    if error_count > max_errors:
        console.print(f"[red]Failed: {error_count} errors > {max_errors}[/red]")
        sys.exit(2)
    if max_warnings and warn_count > max_warnings:
        console.print(f"[yellow]Failed: {warn_count} warnings > {max_warnings}[/yellow]")
        sys.exit(2)

    if all_issues:
        sys.exit(1)
    console.print("[green]No issues found! ✓[/green]")


if __name__ == "__main__":
    cli()