import logging
import sys

from typer import Typer, Option

from .app import NetmonApp


logging.basicConfig(level=logging.WARNING, format="%(name)s %(levelname)s: %(message)s")


app = Typer(no_args_is_help=True)


@app.command()
def main(
    refresh: float = Option(1.0, "--refresh/-r", min=0.1, max=10.0, help="Refresh interval (s)")
) -> None:
    """Launch Netmon TUI network monitor."""

    NetmonApp(refresh_interval=refresh).run(log="textual.log", log_path="logs/")