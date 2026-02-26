import typer
from typing import Optional

from redis_explorer_tui.app import RedisExplorerApp

cli = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)

@cli.command()
def main(
    host: str = typer.Argument("localhost", help="Redis host"),
    port: int = typer.Option(6379, "--port", min=1, max=65535, help="Redis port"),
    db: int = typer.Option(0, "--db", min=0, help="Redis database"),
    password: Optional[str] = typer.Option(None, "--password", help="Redis password"),
    tls: bool = typer.Option(False, "--tls", help="Enable TLS (skip verify)"),
):
    """
    Interactive Redis Explorer TUI
    """
    app = RedisExplorerApp(host, port, password, db, tls)
    app.run()

if __name__ == "__main__":
    cli()
