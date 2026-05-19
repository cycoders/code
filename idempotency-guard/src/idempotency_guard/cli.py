import click
from rich import print
from .core import IdempotencyGuard

@click.group()
def main():
    """Idempotency Guard CLI"""
    pass

@main.command()
@click.argument("key")
def check(key: str):
    guard = IdempotencyGuard()
    print(guard.is_duplicate(key))