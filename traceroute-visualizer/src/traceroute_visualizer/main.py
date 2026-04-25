import subprocess
import sys
import typer
from pathlib import Path
from rich.console import Console
from .parser import parse_traceroute_output
from .enricher import enrich_hop
from .visualizer import print_table, print_histogram, generate_svg, console as viz_console

cli = typer.Typer(add_completion=False, pretty_exceptions_enable=False)

@cli.command()
def main(
    target: str = typer.Argument(None, help="Target host (e.g. google.com)"),
    file: Path = typer.Option(None, "--file", help="Traceroute output file"),
    svg: Path = typer.Option(None, "--svg", help="Export SVG diagram"),
):
    """
    Visualize traceroute: live run or from file.
    """
    if not target and not file:
        typer.echo("Error: Provide TARGET or --file", err=True)
        raise typer.Exit(1)

    text = ""
    if file:
        text = file.read_text()
    else:
        viz_console.print("[bold yellow]Running traceroute -q 3 -n -w 2 -m 30...")
        try:
            result = subprocess.run(
                ["traceroute", "-q", "3", "-n", "-w", "2", "-m", "30", target],
                capture_output=True,
                text=True,
                timeout=120,
                check=True
            )
            text = result.stdout
        except subprocess.CalledProcessError as e:
            typer.echo(f"Traceroute failed: {e.stderr.strip()}", err=True)
            raise typer.Exit(1)
        except FileNotFoundError:
            typer.echo("Error: 'traceroute' not found. Install it (apt/yum/brew).", err=True)
            raise typer.Exit(1)
        except subprocess.TimeoutExpired:
            typer.echo("Traceroute timed out.", err=True)
            raise typer.Exit(1)

    hops = parse_traceroute_output(text)
    if not hops:
        typer.echo("No hops parsed from output.", err=True)
        raise typer.Exit(1)

    viz_console.print("[bold yellow]Enriching hops with WHOIS...")
    for hop in hops:
        enrich_hop(hop)

    print_table(hops)
    print_histogram(hops)

    if svg:
        generate_svg(hops, svg)

if __name__ == "__main__":
    cli()