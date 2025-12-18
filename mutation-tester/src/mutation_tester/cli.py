import typer
from pathlib import Path
from rich import print as rprint
from rich.console import Console

import mutation_tester.config as config
import mutation_tester.runner as runner
from mutation_tester.types import Config


cli_app = typer.Typer(add_completion=False)
console = Console()


@cli_app.command(help="Run mutation testing")
def main(  # noqa: PLR0913
    target_dir: str = typer.Argument(".", help="Project root directory"),
    config_file: str = typer.Option(None, "--config/-c", help="TOML config file"),
    exclude: List[str] = typer.Option([], "--exclude", help="Exclude glob patterns"),
    pytest_args: List[str] = typer.Option(["-q", "--tb=no"], "--pytest-args"),
    timeout: int = typer.Option(30, "--timeout", help="Per-mutant timeout (s)"),
    max_mutants: int = typer.Option(500, "--max-mutants", help="Max mutants to test"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Collect only, no tests"),
    min_score: float = typer.Option(70.0, "--min-score", help="Fail if overall score < this %"),
):
    """Rigorous mutation testing for Python test suites."""
    cfg = config.load_config(
        target_dir,
        config_file,
        exclude,
        pytest_args,
        timeout,
        max_mutants,
        min_score,
        dry_run,
    )
    cfg.target_dir = Path(target_dir)

    try:
        results = runner.run_mutations(cfg.target_dir, cfg, cfg.dry_run)
        console.print(results["table"])
        if not cfg.dry_run:
            score = results["overall_score"]
            color = "green" if score >= cfg.min_score_pct else "red"
            rprint(f"[{color}]Overall kill rate: {score:.1f}%{' (PASS)' if score >= cfg.min_score_pct else ' (FAIL)'}[/]")
            if score < cfg.min_score_pct:
                raise typer.Exit(code=1)
    except Exception as e:
        console.print_exception(show_locals=True)
        typer.echo(f"[red]Error: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    cli_app()