import click
from rich.console import Console
from .analyzer import analyze_file, analyze_directory

console = Console()

@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--format', default='text', type=click.Choice(['text', 'json', 'svg']))
@click.option('--output', default=None, type=click.Path())
def main(path, format, output):
    """Disassemble Python bytecode with rich annotations."""
    if path.endswith('.pyc'):
        result = analyze_file(path, format)
    else:
        result = analyze_directory(path, format)
    if output:
        with open(output, 'w') as f:
            f.write(result)
    else:
        console.print(result)