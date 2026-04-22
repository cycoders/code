import typer
from pathlib import Path
from typing import Optional

import rich.progress
from rich.console import Console

from . import __version__
from .analyzer import analyze
from .config import Config
from .reporter import report, should_fail


app = typer.Typer(add_completion=False)
console = Console()


@app.command(help="Scan for boundary violations")
def scan(
    root: Path = typer.Argument(Path("."), help="Project root to scan"),
    config_file: Path = typer.Option(Path("boundaries.yaml"), "--config", help="Path to YAML config"),
    fail_on: str = typer.Option("error", "--fail-on", choices=["error", "warn"], help="Fail on error or warn"),
    json: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    if not config_file.exists():
        typer.echo(f"Config file not found: {config_file}", err=True)
        raise typer.Exit(1)

    try:
        config = Config.load(config_file)
    except Exception as e:
        typer.echo(f"Invalid config: {e}", err=True)
        raise typer.Exit(1)

    py_files = list(root.glob(f"{config.src_dir}/**/*.py"))
    py_files = [f for f in py_files if not any(fnmatch.fnmatch(str(f.relative_to(root)), pat) for pat in config.ignore_globs)]

    with rich.progress.Progress(console=console) as progress:
        task = progress.add_task("[green]Analyzing files...", total=len(py_files))
        # Note: actual analysis in batches not here for simplicity, progress approximate
        violations = analyze(root, config)
        progress.advance(task, len(py_files))

    report(violations, console, json)

    if should_fail(violations, fail_on):
        raise typer.Exit(1)


@app.command(help="Generate sample config from directory structure")
def init(root: Path = typer.Argument(Path("."), help="Project root")) -> None:
    src_path = root / "src"
    if src_path.exists():
        candidate_dirs = [p.name for p in src_path.iterdir() if p.is_dir()]
    else:
        candidate_dirs = [p.name for p in root.iterdir() if p.is_dir()]

    common_patterns = {
        "utils": "utils.",
        "domain": "domain.",
        "core": "core.",
        "application": "application.",
        "infra": "infra.",
        "adapters": "adapters.",
        "ports": "ports.",
    }

    layers = []
    for name, prefix in common_patterns.items():
        if name in candidate_dirs:
            layers.append(
                {
                    "name": name,
                    "package_prefixes": [prefix],
                    "allowed_layers": [],
                    "forbidden_layers": ["infra"],
                }
            )

    sample_config = {
        "layers": layers,
        "src_dir": "src",
        "allow_third_party": True,
        "ignore_globs": ["**/tests/**", "**/migrations/**"],
    }

    config_path = root / "boundaries.yaml"
    with open(config_path, "w") as f:
        import yaml
        yaml.safe_dump(sample_config, f, default_flow_style=False, sort_keys=False)

    console.print(f"[green]Generated sample config:[/] {config_path}")
    if not layers:
        console.print("[yellow]No common layers detected. Edit manually.[/]")


@app.command(help="Show version")
def version() -> None:
    console.print(f"arch-boundary-auditor {__version__}")


if __name__ == "__main__":
    app()