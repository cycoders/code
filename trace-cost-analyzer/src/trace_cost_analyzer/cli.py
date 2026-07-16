import click
from rich.console import Console
from .analyzer import analyze_traces

console = Console()

@click.command()
@click.option('--input', required=True, type=click.Path(exists=True), help='Trace sample file (JSONL)')
@click.option('--vendor', required=True, type=click.Choice(['datadog','honeycomb','newrelic','grafana','lightstep']))
@click.option('--config', type=click.Path(exists=True), help='Pricing YAML')
def cli(input, vendor, config):
    """Estimate tracing cost from sample traces."""
    result = analyze_traces(input, vendor, config)
    console.print(result)