import typer
from typing_extensions import Annotated

from rich.console import Console

import port_scanner_cli.scanner as scanner
from port_scanner_cli.output import output_results

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
console = Console()

@app.command()
def scan(
    targets: Annotated[str, typer.Argument(..., help="Comma-separated IPs, hostnames, or CIDRs (e.g., '192.168.1.0/24,localhost')")],
    ports: Annotated[str, typer.Option("top100", "-p", help="Ports: preset (top100,common,web,db), comma-list, or range (1-1024)")],
    banner: Annotated[bool, typer.Option(False, "-b", help="Grab banners for fingerprinting")] = False,
    threads: Annotated[int, typer.Option(200, "-t", min=1, max=1000, help="Max threads")] = 200,
    timeout: Annotated[float, typer.Option(1.0, "--timeout", min=0.1, help="Connect timeout (seconds)")] = 1.0,
    output: Annotated[str, typer.Option("table", "-o", help="Output: table, json, csv")] = "table",
):
    """
    Scan targets for open ports with live feedback.
    """
    try:
        ips = scanner.parse_targets(targets)
        ports_list = scanner.parse_ports(ports)
        if not ips:
            raise typer.BadParameter("No valid targets parsed.")
        if not ports_list:
            raise typer.BadParameter("No valid ports parsed.")

        total_probes = len(ips) * len(ports_list)
        console.print(f"[bold blue]Scanning {len(ips)} targets x {len(ports_list)} ports = {total_probes:,} probes...[/]")

        results = scanner.scan_ports(ips, ports_list, banner, threads, timeout, console)

        console.print(f"[bold green]Found {len([r for r in results if r['open']])} open ports![/]")
        output_results(results, output, console)

    except KeyboardInterrupt:
        console.print("\n[red]Scan interrupted.[/]")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e

if __name__ == "__main__":
    app()