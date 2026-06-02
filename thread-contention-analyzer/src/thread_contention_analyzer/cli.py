import click
from .instrument import install
from .reporter import render

@click.command()
@click.option("--duration", default=10)
def main(duration):
    install()
    import time; time.sleep(duration)
    from .wrappers import _contention
    render(_contention)