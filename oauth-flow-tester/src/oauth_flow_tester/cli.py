import typer
from rich.console import Console
from .server import run_server
from .client import run_auth_code_flow, run_client_credentials
from .tokens import inspect_token

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
console = Console()

@app.command(help="Run the mock OAuth 2.0 authorization server")
def server(
    host: str = typer.Option("127.0.0.1", "--host", help="Server host"),
    port: int = typer.Option(8080, "--port", help="Server port"),
):
    """Run the mock OAuth authorization server."""
    console.print(f"🚀 Starting OAuth server at http://{host}:{port}")
    run_server(host, port)

@app.command(help="Run authorization code flow (with auto-browser & callback capture)")
def auth_code(
    server_url: str = typer.Option("http://127.0.0.1:8080", "--server-url"),
    client_id: str = typer.Option("test-client", "--client-id"),
    redirect_uri: str = typer.Option("http://127.0.0.1:9090/callback", "--redirect-uri"),
    scope: str = typer.Option("read", "--scope"),
    pkce: bool = typer.Option(True, "--pkce"),
):
    """Simulate full authorization code flow."""
    console.print("🔄 Running auth code flow...")
    token_data = run_auth_code_flow(server_url, client_id, redirect_uri, scope, pkce, console)
    if token_data:
        inspect_token(token_data["access_token"], console)

@app.command(help="Run client credentials flow")
def client_credentials(
    server_url: str = typer.Option("http://127.0.0.1:8080", "--server-url"),
    client_id: str = typer.Option("test-client", "--client-id"),
    client_secret: str = typer.Option("test-secret", "--client-secret"),
):
    """Obtain token via client credentials."""
    console.print("🔄 Requesting client credentials token...")
    token_data = run_client_credentials(server_url, client_id, client_secret, console)
    if token_data:
        inspect_token(token_data["access_token"], console)

@app.command(help="Inspect and decode a JWT token")
def inspect(token: str):
    """Pretty-print JWT token claims."""
    inspect_token(token, console)

if __name__ == "__main__":  # pragma: no cover
    app()
