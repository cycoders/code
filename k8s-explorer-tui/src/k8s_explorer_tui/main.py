'''CLI entrypoint using Typer. Injects config to TUI.''' 

import logging
import sys
import typer
from typing import Optional

from .client import K8sExplorerClient
from .tui import ExplorerApp


cli = typer.Typer(help="Interactive Kubernetes Explorer TUI")


@cli.command()
def main(
    context: Optional[str] = typer.Option(None, "--context", help="Kubeconfig context"),
    namespace: Optional[str] = typer.Option(None, "--namespace", help="Default namespace"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Launch K8s Explorer TUI."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=level
    )

    try:
        client = K8sExplorerClient(context=context, default_namespace=namespace)
        app = ExplorerApp(client)
        app.run()
    except Exception as e:
        typer.echo(f"✗ {e}", err=True, color=typer.colors.RED)
        sys.exit(1)


if __name__ == "__main__":
    main()