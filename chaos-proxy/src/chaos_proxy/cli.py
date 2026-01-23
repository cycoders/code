import typer

from .config import Config, load_config_from_cli, load_config_from_yaml
from .server import run_server

app = typer.Typer(no_args_is_help=True)

@app.command(help="Start the chaos proxy server")
def serve(
    target: str = typer.Argument(..., help="Target host:port (e.g. httpbin.org:80)"),
    local_port: int = typer.Option(8080, "--local-port", "-p", min=1, max=65535),
    latency: str = typer.Option("0ms", "--latency", "-l", help="Base latency (e.g. 100ms, 1s)"),
    jitter: str = typer.Option("0ms", "--jitter", "-j", help="Jitter range (e.g. 50ms)"),
    loss: float = typer.Option(0.0, "--loss", "-s", min=0.0, max=1.0, help="Packet loss fraction (0.02 = 2%)"),
    dup: float = typer.Option(0.0, "--dup", "-d", min=0.0, max=1.0, help="Duplication fraction"),
    bw: str = typer.Option("inf", "--bw", "-b", help="Bandwidth limit kbps (e.g. 100, inf)"),
    config: typer.FilePath(None, "--config", "-c") = None,
):
    """
    Serve a TCP proxy with network impairments.

    Example::

        chaos-proxy serve httpbin.org:80 8080 --latency 200ms --loss 0.02
        curl -x http://localhost:8080 https://httpbin.org/get
    """
    try:
        if config:
            cfg = load_config_from_yaml(config)
        else:
            cfg = load_config_from_cli(target, local_port, latency, jitter, loss, dup, bw)
        typer.echo(f"🚀 Starting chaos proxy: localhost:{cfg.local_port} -> {cfg.target_host}:{cfg.target_port}")
        typer.echo(f"   Impairments: latency={cfg.latency*1000:.0f}ms ±{cfg.jitter*1000:.0f}ms, loss={cfg.loss:.1%}, "
                   f"dup={cfg.dup:.1%}, bw={cfg.bw_kbps:.0f}kbps", err=True)
        run_server(cfg)
    except KeyboardInterrupt:
        typer.echo("\n👋 Shutting down gracefully.")
    except Exception as e:
        typer.secho(f"💥 Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
