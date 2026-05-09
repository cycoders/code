import logging
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich import print as rprint
from rich.traceback import install

install(show_locals=True)

try:
    from . import __version__
except ImportError:
    __version__ = "dev"

from .config import load_config, ScanConfig, save_config

from .scanner import Scanner

from .resource_classifier import classify_resources

from .policy_generator import generate_csp, strictness_score

from .reporter import report_resources, audit, console, progress


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


app = typer.Typer(add_completion=False)


@app.command(name="scan")
def scan_command(
    urls: List[str] = typer.Argument(..., help="URLs to scan"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="YAML config"),
    max_depth: int = typer.Option(2, "--max-depth", help="Max recursion depth"),
    max_pages: int = typer.Option(50, "--max-pages", help="Max pages to scan"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save policy to file"),
    audit_policy: Optional[str] = typer.Option(None, "--audit", help="Audit against this policy"),
    prefer_hashes: bool = typer.Option(True, "--prefer-hashes", help="Use hashes over unsafe-inline"),
    version: bool = typer.Option(False, "--version"),
) -> None:
    """Scan sites and generate CSP policy."""

    if version:
        rprint(f"csp-policy-builder {__version__}")
        raise typer.Exit(0)

    # Config
    config = ScanConfig(urls=urls, max_depth=max_depth, max_pages=max_pages)
    if config_file:
        config = load_config(config_file)

    # Scan with progress
    with progress:
        task = progress.add_task("Scanning...", total=None)
        scanner = Scanner(config)
        raw_resources = scanner.scan()
        progress.remove_task(task)

    resources = classify_resources(raw_resources)

    # Generate
    policy = generate_csp(resources, prefer_hashes)
    score = strictness_score(policy)

    # Report
    report_resources(resources, policy, score)

    if audit_policy:
        audit(resources, audit_policy)

    # Output file
    if output:
        output.write_text(policy)
        rprint(f"[green]Policy saved to {output}[/]")


if __name__ == "__main__":  # pragma: no cover
    app(prog_name="csp-policy-builder")
