import typer
from pathlib import Path
from typing import Optional

import rich.progress
from rich.progress import Progress

from .config import load_config
from .transpiler import SQLTranspiler
from .reporter import report_summary


app = typer.Typer(help="Transpile SQL between dialects.")


@app.command()
def transpile(  # noqa: PLR0913
    input_path: Path = typer.Argument(..., help="SQL file or directory"),
    from_dialect: str = typer.Option("postgres", "--from", "-f", help="Source dialect"),
    to_dialect: str = typer.Option("mysql", "--to", "-t", help="Target dialect"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output dir"),
    in_place: bool = typer.Option(False, "--in-place", "-i"),
    dry_run: bool = typer.Option(True, "--dry-run", help="Preview diffs"),
    validate: bool = typer.Option(False, "--validate", "-v"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
    json: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Transpile SQL files/directories."""

    if in_place and output is not None:
        raise typer.BadParameter("--in-place incompatible with --output")

    # Config
    config = load_config(config_file) if config_file else {}
    cfg = {
        **config.get("defaults", {}),
        "from": from_dialect,
        "to": to_dialect,
        "validate": validate,
    }

    trans = SQLTranspiler(cfg["from"], cfg["to"])

    # Files
    is_dir = input_path.is_dir()
    base_path = input_path if is_dir else input_path.parent
    files = list(input_path.rglob("*.sql")) if is_dir else [input_path]

    if not files:
        typer.echo("No .sql files found.", err=True)
        raise typer.Exit(1)

    # Process
    results = []
    with Progress() as progress:
        task = progress.add_task("[cyan]Transpiling...", total=len(files))
        for fpath in files:
            try:
                original = fpath.read_text(encoding="utf-8")
                transpiled, issues = trans.transpile(original)
                changed = original != transpiled
                success = len(issues) == 0 and not any("error" in str(i) for i in issues)
                results.append(
                    {
                        "file": str(fpath),
                        "success": success,
                        "issues": issues,
                        "original": original,
                        "transpiled": transpiled,
                        "changed": changed,
                    }
                )
            except Exception as e:
                results.append({"file": str(fpath), "success": False, "error": str(e)})
            progress.advance(task)

    report_summary(results, dry_run, output, in_place, json, base_path)


if __name__ == "__main__":
    app()