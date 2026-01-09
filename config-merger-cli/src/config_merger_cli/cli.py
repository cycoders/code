import typer
from typing import List

from rich.console import Console

from .loader import load_config
from .merger import deep_merge, parse_strategy
from .env import apply_env_overrides
from .dumper import dump_config


app = typer.Typer(add_completion=False)
console = Console()


@app.command(help="Merge layered config files with optional strategy and env overrides.")
def merge(
    files: List[str] = typer.Argument(
        ..., help="Config files to merge (later files override earlier)"
    ),
    output: str = typer.Option("-", "--output", "-o", help="Output file (- for stdout)"),
    strategy: str = typer.Option(
        "lists=append,dicts=merge",
        "--strategy",
        "-s",
        help="Strategy: lists=<append|prepend|union|replace>,dicts=<merge|replace>",
    ),
    fmt: str = typer.Option("yaml", "--format", "-f", help="Output: yaml|json|toml"),
    env_prefix: str = typer.Option(
        None, "--env-prefix", help="Env prefix for overrides (nested: APP__KEY__SUB=val)"
    ),
) -> None:
    """Merge config files into one."""
    if not files:
        raise typer.BadParameter("Provide at least one config file.")

    try:
        configs = [load_config(f) for f in files]
        strat = parse_strategy(strategy)
        merged = configs[0]
        for config in configs[1:]:
            deep_merge(merged, config, strat)
        if env_prefix:
            apply_env_overrides(merged, env_prefix)
        dump_config(merged, output, fmt)
    except Exception as exc:
        console.print(f"[red bold]Error:[/red bold] {exc}", file=sys.stderr)
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()