import click
from rich.console import Console
from crypto_agility_scanner.scanner import scan_path
from crypto_agility_scanner.formatters import render

console = Console()

@click.group()
def main():
    pass

@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--format", default="text", type=click.Choice(["text", "json", "sarif"]))
@click.option("--output", type=click.Path(), default=None)
@click.option("--fail-on", default="critical")
def scan(path, format, output, fail_on):
    findings = scan_path(path)
    render(findings, format, output, console)
    if any(f.severity == fail_on for f in findings):
        raise click.Abort()