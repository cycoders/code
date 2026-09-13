import click
from rich.console import Console
from .engine import AntiPatternVisitor
import libcst as cst

console = Console()

@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--fix", is_flag=True)
def main(paths, fix):
    for path in paths:
        with open(path) as f:
            tree = cst.parse_module(f.read())
        visitor = AntiPatternVisitor()
        tree.walk(visitor)
        for f in visitor.findings:
            console.print(f"{path}:{f.line}:{f.col} [{f.severity}] {f.rule}: {f.message}")