import jwt
import time
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from .types import TokenDict

SECRET_KEY = "oauth-flow-tester-secret-2025-change-in-production"
ALGO = "HS256"


def generate_access_token(client_id: str, scope: str = "") -> str:
    """Generate signed JWT access token."""
    now = datetime.utcnow()
    payload = {
        "sub": client_id,
        "scope": scope,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
        "iss": "https://oauth-flow-tester.local",
        "aud": client_id,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)


def inspect_token(token: str, console: Console) -> None:
    """Decode and pretty-print token claims."""
    try:
        # Decode without verification first
        unverified = jwt.decode(token, options={ "verify_signature": False })
        # Verify signature
        verified = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
        table = Table(title="[bold green]JWT Token Claims[/bold green]", show_header=True, header_style="bold magenta")
        table.add_column("Claim", style="cyan")
        table.add_column("Value", style="white")
        for key, value in verified.items():
            table.add_row(key, str(value))
        console.print(table)
        console.print(f"[green]✅ Signature valid. Expires: {datetime.fromtimestamp(verified['exp'])}[/green]")
    except jwt.InvalidTokenError as e:
        console.print(f"[red]❌ Invalid token: {str(e)}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Decode error: {str(e)}[/red]")
