import click
from rich.console import Console
from .parser import parse_folded
from .diff import compute_diff
from .render import render_terminal, render_html

console = Console()

@click.command()
@click.argument('before', type=click.Path(exists=True))
@click.argument('after', type=click.Path(exists=True))
@click.option('--alpha', default=0.01, help='Significance threshold')
@click.option('--format', 'fmt', default='terminal', type=click.Choice(['terminal', 'html']))
@click.option('--output', type=click.Path())
def main(before, after, alpha, fmt, output):
    """Statistical flamegraph diffing CLI."""
    stacks_before = parse_folded(before)
    stacks_after = parse_folded(after)
    result = compute_diff(stacks_before, stacks_after, alpha)
    if fmt == 'terminal':
        render_terminal(result, console)
    else:
        html = render_html(result)
        if output:
            open(output, 'w').write(html)
        else:
            print(html)
    if result.regressions:
        raise SystemExit(1)