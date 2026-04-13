import sys
import pathlib
from typing import List

import typer
import yaml
import rich_click as click

from k8s_netpol_sim import __version__
from k8s_netpol_sim.models import Topology
from k8s_netpol_sim.simulator import simulate
from k8s_netpol_sim.visualizer import print_result, mermaid_graph


app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")


@app.command(name="sim")
def sim_command(
    topology_file: pathlib.Path = typer.Argument(..., help="Topology YAML"),
    policies_file: pathlib.Path = typer.Argument(..., help="Policies YAML"),
    from_: str = typer.Argument(..., help="Source: <namespace>/<pod>"),
    to: str = typer.Argument(..., help="Destination: <namespace>/<pod>"),
    port: int = typer.Option(80, "--port", "-p", help="Port"),
    protocol: str = typer.Option("TCP", "--protocol", "-proto", help="Protocol"),
    output: str = typer.Option("table", "--output", "-o", help="table | mermaid | json"),
):
    """Simulate NetworkPolicy flow."""
    try:
        with topology_file.open() as f:
            topo_data = yaml.safe_load(f)
        topology = Topology.model_validate(topo_data)

        with policies_file.open() as f:
            pol_data = yaml.safe_load(f)
        policies = [m.NetPol.model_validate(p) for p in pol_data]

        src_ns, src_pod = from_.split("/", 1)
        dst_ns, dst_pod = to.split("/", 1)

        allowed, details = simulate(topology, policies, src_ns, src_pod, dst_ns, dst_pod, port, protocol)

        if output == "json":
            print(yaml.dump({"allowed": allowed, **details}))
            raise typer.Exit(0 if allowed else 1)
        elif output == "mermaid":
            print(mermaid_graph(details, allowed))
        else:
            print_result(allowed, details)

        raise typer.Exit(0 if allowed else 1)
    except Exception as e:
        typer.echo(f"[red]Error:[/red] {e}", err=True)
        raise typer.Exit(1) from e


@app.command()
def version():
    """Show version."""
    typer.echo(f"k8s-netpol-sim {__version__}")


if __name__ == "__main__":
    app(prog_name="k8s-netpol-sim")


if __name__ == "__main__":
    app()