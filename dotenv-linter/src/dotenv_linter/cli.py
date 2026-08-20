import click
from rich.console import Console
from pathlib import Path
from dotenv_linter.parser import parse_env
from dotenv_linter.rules import duplicate_keys

console = Console()

@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--fix", is_flag=True)
def cli(paths, fix):
    for p in paths or [Path(".env")]:
        entries = parse_env(Path(p))
        violations = duplicate_keys(entries)
        for v in violations:
            console.print(f"{p}:{v.line} {v.message}")