import asyncio
import json
import os
import tomllib
from pathlib import Path
from typing import Annotated, Optional

import typer
from loguru import logger
from rich.console import Console

from .config import load_config
from .models import Config, RateLimitInfo
from .tester import RateLimitTester
from .visualizer import live_dashboard

app = typer.Typer(add_completion=False, context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
console = Console()

@app.command(name="discover")
def discover_cmd(
    url: str,
    auth_token: Optional[str] = typer.Option(None, "--auth-token", envvar="RLT_AUTH_TOKEN"),
    auth_user: Optional[str] = typer.Option(None, "--auth-user"),
    auth_pass: Optional[str] = typer.Option(None, "--auth-pass", hide_input=True),
    headers: list[str] = typer.Option([], "--header"),
    config_file: Path = typer.Option(Path("~/.config/rate-limit-tester/config.toml"), "--config"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
    output: Optional[Path] = typer.Option(None, "--output"),
):
    """Discover rate limits from response headers (safe, no stress)."""
    if verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    cfg = load_config(config_file, overrides={"url": url, "auth_token": auth_token})
    tester = RateLimitTester.from_config(cfg)

    async def run():
        info = await tester.discover()
        console.print(info.rich_table())
        if output:
            output.write_text(info.model_dump_json(indent=2))
        return info

    asyncio.run(run())


@app.command()
def burst_cmd(
    url: str,
    concurrency_max: Annotated[int, typer.Argument(..., min=1)] = 100,
    auth_token: Optional[str] = typer.Option(None),
    config_file: Path = typer.Option(Path("~/.config/rate-limit-tester/config.toml"), "--config"),
    verbose: bool = False,
):
    """Binary search for max burst capacity."""
    if verbose:
        logger.add(sys.stderr, level="DEBUG")

    cfg = load_config(config_file, overrides={"url": url, "auth_token": auth_token})
    tester = RateLimitTester.from_config(cfg)

    async def run():
        burst = await tester.measure_burst(concurrency_max)
        console.print(f"[bold green]Max burst capacity: {burst}"[bold green])

    asyncio.run(run())


@app.command()
def sustained_cmd(
    url: str,
    duration: Annotated[int, typer.Argument(..., min=1)] = 60,
    concurrency: Annotated[int, typer.Argument(..., min=1)] = 10,
    auth_token: Optional[str] = typer.Option(None),
    config_file: Path = typer.Option(Path("~/.config/rate-limit-tester/config.toml"), "--config"),
    verbose: bool = False,
):
    """Measure sustained reqs/sec over duration."""
    if verbose:
        logger.add(sys.stderr, level="DEBUG")

    cfg = load_config(config_file, overrides={"url": url, "auth_token": auth_token, "duration": duration, "concurrency": concurrency})
    tester = RateLimitTester.from_config(cfg)

    async def run():
        stats = await tester.sustained_test()
        console.print(stats)

    asyncio.run(run())


@app.command()
def test_cmd(
    url: str,
    config_file: Path = typer.Option(Path("~/.config/rate-limit-tester/config.toml"), "--config"),
    verbose: bool = False,
):
    """Full test: discover + burst + sustained + reset."""
    if verbose:
        logger.add(sys.stderr, level="DEBUG")

    cfg = load_config(config_file, overrides={"url": url})
    tester = RateLimitTester.from_config(cfg)

    async def run():
        with live_dashboard():
            info = await tester.discover()
            console.print("[bold]Discovery:[/bold]")
            console.print(info.rich_table())

            burst = await tester.measure_burst()
            console.print(f"[bold]Burst:[/bold] {burst}")

            stats = await tester.sustained_test()
            console.print(f"[bold]Sustained:[/bold] {stats.avg_rps:.2f} rps")

            reset = await tester.measure_reset()
            console.print(f"[bold]Reset time:[/bold] {reset}s")

    asyncio.run(run())


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    config_file: Optional[Path] = typer.Option(None, "--config"),
):
    """Rate Limit Tester: Discover & stress-test API quotas precisely.\n\n    Examples: rate-limit-tester discover https://api.github.com/user"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(test_cmd, url="https://httpbin.org/json")
