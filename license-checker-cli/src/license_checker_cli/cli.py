import typer
import os
from pathlib import Path
from typing_extensions import Annotated

from .config import load_config
from .detectors import detect_all_deps
from .output import print_report
from .policies import apply_policy

app = typer.Typer(help="Audit OSS licenses in project deps.")

@app.command(help="Scan deps and print license report.")
def scan(
    path: Annotated[Path, typer.Argument(Path("."), help="Project root")] = ".",
    config: Annotated[Path, typer.Option(Path(".license-checker.toml"), "--config")] = ".license-checker.toml",
    fmt: Annotated[str, typer.Option("table", "--format", help="table|json|markdown")] = "table",
):
    """Scan project for dependency licenses."""
    cfg = load_config(config) if config.exists() else {}
    deps = detect_all_deps(path)
    report = apply_policy(deps, cfg)
    print_report(report, fmt)

@app.command(help="Check deps against policy (exit 1 on violations).")
def check(
    path: Annotated[Path, typer.Argument(Path("."), help="Project root")] = ".",
    config: Annotated[Path, typer.Option(Path(".license-checker.toml"), "--config")] = ".license-checker.toml",
):
    """Fail if policy violations found."""
    cfg = load_config(config) if config.exists() else {}
    deps = detect_all_deps(path)
    report = apply_policy(deps, cfg)
    violations = [d for d in report if not d.approved]
    if violations:
        typer.secho("❌ License violations:", fg=typer.colors.RED, bold=True)
        print_report(violations, "table")
        raise typer.Exit(code=1)
    typer.secho("✅ All licenses approved.", fg=typer.colors.GREEN)

if __name__ == "__main__":
    app()