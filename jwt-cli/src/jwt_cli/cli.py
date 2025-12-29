import typer
import sys
import json
from typing import Optional

from rich.console import Console

console = Console()

from .jwt_ops import decode_token, sign_token, validate_token
from .output import display_decoded

app = typer.Typer(
    help="Secure offline CLI for JWT decode/sign/validate.",
    no_args_is_help=True,
)

@app.command("decode", help="Decode JWT (unverified).")
def decode_cmd(
    token: str = typer.Argument(..., help="JWT token"),
    json_out: bool = typer.Option(False, "--json/-j"),
):
    """Decode and display JWT header/payload/signature."""
    try:
        header, payload, sig_b64 = decode_token(token)
        if json_out:
            data = {"header": header, "payload": payload, "signature_b64": sig_b64}
            console.print_json(data=data, indent=2)
        else:
            display_decoded(header, payload, sig_b64)
    except Exception as e:
        console.print(f"[red bold]Error:[/red bold] {str(e)}")
        raise typer.Exit(1)

@app.command("sign", help="Sign payload to JWT.")
def sign_cmd(
    payload_file: typer.FileText = typer.Argument(..., help="Payload JSON (- for stdin)"),
    key: str = typer.Option("", "--key/-k", help="Key secret"),
    key_file: Optional[typer.FileBinary] = typer.Option(None, "--key-file"),
    alg: str = typer.Option("HS256", "--alg/-a"),
    header_file: Optional[typer.FileText] = typer.Option(None, "--header-file"),
):
    """Create signed JWT from payload."""
    try:
        payload_str = payload_file.read().strip()
        payload = json.loads(payload_str)

        headers = {}
        if header_file:
            headers = json.loads(header_file.read())

        if key_file:
            key_data = key_file.read()
        else:
            if not key:
                raise typer.BadParameter("--key or --key-file required")
            key_data = key.encode("utf-8")

        token = sign_token(payload, key_data, alg, headers)
        console.print(token)
    except json.JSONDecodeError as e:
        typer.echo(f"JSON error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red bold]Sign error:[/red bold] {str(e)}")
        raise typer.Exit(1)

@app.command("validate", help="Validate JWT sig/claims.")
def validate_cmd(
    token: str = typer.Argument(..., help="JWT token"),
    key: str = typer.Option("", "--key/-k"),
    key_file: Optional[typer.FileBinary] = typer.Option(None, "--key-file"),
    alg: Optional[str] = typer.Option(None, "--alg"),
    issuer: Optional[str] = typer.Option(None, "--issuer/-i"),
    audience: Optional[str] = typer.Option(None, "--audience/-u"),
    leeway: int = typer.Option(0, "--leeway/-l"),
):
    """Check signature, exp, iss, aud, etc."""
    try:
        if key_file:
            key_data = key_file.read()
        else:
            if not key:
                raise typer.BadParameter("--key or --key-file required")
            key_data = key.encode("utf-8")

        valid, errors = validate_token(token, key_data, alg, issuer, audience, leeway)
        if valid:
            console.print("[green bold]✅ VALID[/]")
        else:
            console.print("[red bold]❌ INVALID[/]")
            for err in errors:
                console.print(f"  [red]✗ {err}[/]", highlight=False)
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red bold]Validate error:[/red bold] {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()