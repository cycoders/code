from __future__ import annotations

import json
import sys

from rich.console import Console

import click

from histogram_merger.ddsketch import DDSketch

from histogram_merger.merge import merge_sketches

console = Console()


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--p99", is_flag=True, help="Show p99")
def merge(files: tuple[str], p99: bool) -> None:
    sketches = []
    for f in files:
        data = json.loads(open(f).read())
        sk = DDSketch()
        for v, c in data.items():
            sk.add(float(v), c)
        sketches.append(sk)
    merged = merge_sketches(sketches)
    if p99:
        console.print(merged.quantile(0.99))