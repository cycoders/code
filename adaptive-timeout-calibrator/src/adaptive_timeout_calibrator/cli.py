import click, json, yaml
from rich.console import Console
from .models import LatencyHistogram
from .fitter import fit_and_recommend

console = Console()

@click.command()
@click.argument("histogram", type=click.Path(exists=True))
@click.option("--slo", default=0.999, type=float)
@click.option("--budget", default=0.01, type=float)
@click.option("--output", type=click.Path())
def cli(histogram, slo, budget, output):
    """Calculate adaptive timeouts from latency histogram."""
    with open(histogram) as f:
        raw = json.load(f)
    hist = LatencyHistogram(**raw)
    rec = fit_and_recommend(hist, slo, budget)
    console.print(rec.model_dump_json(indent=2))
    if output:
        with open(output, "w") as f:
            yaml.dump(rec.model_dump(), f)