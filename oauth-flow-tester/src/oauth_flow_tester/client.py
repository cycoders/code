import httpx
import threading
import time
import webbrowser
from urllib.parse import urlencode, parse_qs
from flask import Flask, request
from rich.console import Console
from rich.progress import Progress
from .utils import generate_state, generate_pkce_pair
from .types import TokenDict


def run_auth_code_flow(
    server_url: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    use_pkce: bool,
    console: Console,
) -> TokenDict | None:
    """Run full auth code flow with browser and callback server."""
    state = generate_state()
    verifier = challenge = None
    if use_pkce:
        verifier, challenge = generate_pkce_pair()

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
    }
    if challenge:
        params.update({"code_challenge": challenge, "code_challenge_method": "S256"})

    auth_url = f"{server_url}/auth?{urlencode(params)}"

    code = [None]
    captured_state = [None]

    def create_callback_app():
        cb_app = Flask(__name__)

        @cb_app.route("/callback")
        def callback():
            query = parse_qs(request.query_string.decode())
            code[0] = query.get("code", [None])[0]
            captured_state[0] = query.get("state", [None])[0]
            return """
            <html>
                <body style='font-family: Arial;'>
                    <h1>✅ OAuth Success!</h1>
                    <p>Code captured. <strong>You can close this tab.</strong></p>
                    <script>window.close();</script>
                </body>
            </html>
            """

        return cb_app

    # Start callback server
    callback_app = create_callback_app()
    server_thread = threading.Thread(
        target=lambda: callback_app.run(host="127.0.0.1", port=9090, debug=False, use_reloader=False)
    )
    server_thread.daemon = True
    server_thread.start()

    time.sleep(1)  # Ensure server up
    console.print("🌐 Starting callback listener at http://127.0.0.1:9090/callback")
    console.print(f"🔗 [blue]Auth URL[/blue]: {auth_url}")

    with Progress(console=console) as progress:
        task = progress.add_task("Waiting for redirect...", total=None)
        webbrowser.open(auth_url)

        while code[0] is None:
            time.sleep(0.5)
            progress.update(task, description="Waiting for auth code...")

        progress.update(task, completed=100)

    if captured_state[0] != state:
        console.print("[red]❌ State mismatch![/red]")
        return None

    # Exchange code for token
    data = {
        "grant_type": "authorization_code",
        "code": code[0],
        "client_id": client_id,
        "redirect_uri": redirect_uri,
    }
    if verifier:
        data["code_verifier"] = verifier

    with httpx.Client() as client:
        resp = client.post(f"{server_url}/token", data=data, timeout=10.0)

    if resp.status_code == 200:
        console.print("[green]✅ Token obtained![/green]")
        return resp.json()
    else:
        console.print(f"[red]❌ Token exchange failed: {resp.json()}[/red]")
        return None


def run_client_credentials(
    server_url: str, client_id: str, client_secret: str, console: Console
) -> TokenDict | None:
    """Fetch token via client credentials."""
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    with httpx.Client() as client:
        resp = client.post(f"{server_url}/token", data=data, timeout=10.0)
    if resp.status_code == 200:
        return resp.json()
    console.print(f"[red]❌ Failed: {resp.status_code} - {resp.text}[/red]")
    return None
