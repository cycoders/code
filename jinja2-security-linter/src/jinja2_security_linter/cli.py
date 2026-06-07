import click
from rich.console import Console
from .scanner import scan_directory

console = Console()

@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--fix", is_flag=True, help="Apply safe autofixes")
@click.option("--format", type=click.Choice(["text", "json", "sarif"]), default="text")
def main(path: str, fix: bool, format: str) -> None:
    """Run the Jinja2 security linter."""
    findings = scan_directory(path, fix=fix)
    if format == "text":
        for f in findings:
            console.print(f"[red]{f.rule}[/red] {f.file}:{f.line} - {f.message}")
    else:
        console.print_json(findings)
    raise SystemExit(1 if findings else 0)