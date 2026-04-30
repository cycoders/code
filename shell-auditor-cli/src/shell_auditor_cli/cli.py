import typer
from pathlib import Path
from typing import Annotated, Literal, Optional

from .config import load_config
from .core import audit
from .fixer import apply_fixes
from .reporter import report
from .types import AuditResult


app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def audit(  # noqa: PLR0913
    path: Annotated[
        Path,
        typer.Argument(
            ...,
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    fix: Annotated[bool, typer.Option(False, "--fix", help="Apply safe auto-fixes")] = False,
    output: Annotated[
        Literal["rich", "json", "md"],
        typer.Option("rich", "--output/-o", help="Output format"),
    ] = "rich",
    config_file: Annotated[Optional[Path], typer.Option(None, "--config", help="Config TOML")] = None,
    no_config: Annotated[bool, typer.Option(False, "--no-config", help="Ignore config")] = False,
) -> None:
    """Audit a shell script for issues."""

    # Load config
    if no_config:
        config = {}
    else:
        config = load_config()
        if config_file:
            import tomli

            with open(config_file, "rb") as f:
                config = tomli.load(f)

    # Audit
    result: AuditResult = audit(path, config)

    # Report
    report(result, output)

    # Fix if requested
    if fix:
        apply_fixes(path, result.issues)


def main() -> None:
    """Entry point for console_scripts."""
    app(prog_name="shell-auditor-cli")


if __name__ == "__main__":
    main()