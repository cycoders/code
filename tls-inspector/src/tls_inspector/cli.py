import asyncio
import json
import typer
from tls_inspector.inspector import inspect_tls
from tls_inspector.models import TLSReport
from tls_inspector.output import render_report


cli = typer.Typer(add_completion=False)


@cli.command()
def inspect(
    host: str,
    port: int = typer.Option(443, "--port/-p", min=1, max=65535),
    ipv6: bool = typer.Option(False, "--ipv6"),
    json_output: bool = typer.Option(False, "--json"),
):
    """
    Inspect TLS/SSL configuration of a remote HTTPS endpoint.
    """
    try:
        report: TLSReport = asyncio.run(inspect_tls(host, port, ipv6))
        if json_output:
            print(json.dumps(report.__dict__, default=str, indent=2))
        else:
            render_report(report)
    except ValueError as exc:
        typer.echo(f"[red]Error:[/] {exc}", err=True)
        raise typer.Exit(code=1) from exc
    except KeyboardInterrupt:
        typer.echo("\n[red]Interrupted[/]")
        raise typer.Exit(code=130)


if __name__ == "__main__":
    cli()