'''CLI entrypoint for curl-to-python.''' 

import typer

from .parser import parse_curl
from .renderer import parsed_to_code


app = typer.Typer(add_completion=False)

@app.command(help="Convert curl to Python code")
def main(  # pylint: disable=too-many-arguments
    curl_command: str = typer.Argument(..., help="Full curl command"),
    httpx: bool = typer.Option(False, "--httpx", help="Use httpx (sync/async)"),
    async_: bool = typer.Option(
        False, "--async", help="Async code (httpx only)"
    ),
    output: typer.TextIO = typer.Option(
        "-", "--output", "-o", help="Output file (default: stdout)"
    ),
) -> None:
    """Main CLI handler."""

    if async_ and not httpx:
        raise typer.BadParameter("--async requires --httpx")

    try:
        parsed = parse_curl(curl_command)
        code = parsed_to_code(parsed, httpx=httpx, async_=async_)
        print(code, file=output, end="")
    except ValueError as exc:
        typer.echo(f"Parse error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    except Exception as exc:  # pylint: disable=broad-except
        typer.echo(f"Unexpected error: {exc}", err=True)
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
