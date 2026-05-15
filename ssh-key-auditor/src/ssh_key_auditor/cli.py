import typer
from pathlib import Path
from typing import Optional

from .auditor import scan_ssh_dir
from .reporter import report


app = typer.Typer(help="SSH Key Auditor: Secure your keys.")


@app.command(help="Scan SSH directory for issues")
def scan(
    path: Path = typer.Argument(Path.home() / ".ssh", help="SSH directory"),
    output: str = typer.Option("table", "--output/-o", help="Output format (table|json|html)"),
    output_file: Optional[Path] = typer.Option(None, "--output-file/-f", help="Save report to file"),
):
    """
    Audit SSH keys for security issues.
    """
    if output not in ("table", "json", "html"):
        typer.echo("Invalid output: table|json|html", err=True)
        raise typer.Exit(1)

    try:
        issues = scan_ssh_dir(path)
        report(issues, output, output_file)
        if issues:
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error scanning {path}: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

def main():
    app(prog_name="ssh-key-auditor")
