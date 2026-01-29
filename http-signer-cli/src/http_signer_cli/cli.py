import typer
from pathlib import Path
from typing import Optional, Annotated, Literal
from .config import get_credentials
from .parsers import parse_curl
from .output import generate_curl_command, print_curl
from .signers.aws4 import sign_aws4
from .signers.oauth1 import sign_oauth1

app = typer.Typer(help="HTTP request signer CLI", no_args_is_help=True)
console = typer.console

aws_app = typer.Typer()

@aws_app.command(name="sign")
def aws4_sign(
    url: str,
    method: str = "GET",
    headers: Annotated[list[str], typer.Option()] = [],
    data: str = "",
    region: str,
    service: str,
    access_key: str,
    secret_key: str,
    session_token: Optional[str] = None,
    profile: Optional[str] = None,
    from_curl: Optional[str] = typer.Option(None, "--from-curl"),
    exec_: bool = typer.Option(False, "--exec"),
):
    """Sign AWS SigV4 request."""
    if profile:
        creds = get_credentials(profile, "aws4")
        access_key = creds.get("access_key", access_key)
        secret_key = creds.get("secret_key", secret_key)
        region = creds.get("default_region", region)
        service = creds.get("default_service", service)
        session_token = creds.get("session_token", session_token)

    header_dict = {h.split(":", 1)[0].strip(): h.split(":", 1)[1].strip() for h in headers}

    if from_curl:
        parsed = parse_curl(from_curl)
        method = parsed["method"]
        url = parsed["url"]
        header_dict = parsed["headers"]
        data = parsed["body"]

    body_bytes = data.encode("utf-8")
    signed_headers = sign_aws4(method, url, header_dict, body_bytes, access_key, secret_key, region, service, session_token)

    curl_cmd = generate_curl_command(method, url, signed_headers, data)
    print_curl(curl_cmd)

    if exec_:
        from typer.confirm import Confirm
        if Confirm.ask("Execute the signed request?"):
            import subprocess
            import shlex
            subprocess.run(shlex.split(" ".join(curl_cmd)), check=True)

oauth_app = typer.Typer()

@oauth_app.command(name="sign")
def oauth1_sign(
    url: str,
    method: str = "GET",
    headers: Annotated[list[str], typer.Option()] = [],
    data: str = "",
    consumer_key: str,
    consumer_secret: str,
    access_token: Optional[str] = None,
    token_secret: Optional[str] = None,
    realm: Optional[str] = None,
    profile: Optional[str] = None,
    from_curl: Optional[str] = typer.Option(None, "--from-curl"),
    exec_: bool = typer.Option(False, "--exec"),
):
    """Sign OAuth 1.0a request."""
    if profile:
        creds = get_credentials(profile, "oauth1")
        consumer_key = creds.get("consumer_key", consumer_key)
        consumer_secret = creds.get("consumer_secret", consumer_secret)
        access_token = creds.get("access_token", access_token)
        token_secret = creds.get("token_secret", token_secret)

    header_dict = {h.split(":", 1)[0].strip(): h.split(":", 1)[1].strip() for h in headers}

    if from_curl:
        parsed = parse_curl(from_curl)
        method = parsed["method"]
        url = parsed["url"]
        header_dict = parsed["headers"]
        data = parsed["body"]

    body_bytes = data.encode("utf-8")
    signed_headers = sign_oauth1(method, url, header_dict, body_bytes, consumer_key, consumer_secret, access_token, token_secret, realm)

    curl_cmd = generate_curl_command(method, url, signed_headers, data)
    print_curl(curl_cmd)

    if exec_:
        from typer.confirm import Confirm
        if Confirm.ask("Execute the signed request?"):
            import subprocess
            import shlex
            subprocess.run(shlex.split(" ".join(curl_cmd)), check=True)

app.add_typer("aws4", aws_app, hidden=False)
app.add_typer("oauth1", oauth_app, hidden=False)

if __name__ == "__main__":
    app()