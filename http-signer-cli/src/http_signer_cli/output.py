import shlex
import pyperclip
from rich.console import Console
from rich.panel import Panel

console = Console()

def generate_curl_command(method: str, url: str, headers: dict, body: str) -> list[str]:
    """Generate executable curl command list."""
    cmd = ["curl", "-X", method, url]
    for key, value in sorted(headers.items()):
        cmd += ["-H", f"{key}: {value}"]
    if body:
        cmd += ["-d", body]
    return cmd

def print_curl(cmd: list[str]) -> None:
    """Print rich curl, copy to clipboard."""
    full_cmd = " ".join(shlex.quote(arg) for arg in cmd)
    pyperclip.copy(full_cmd)
    console.print(Panel(full_cmd, title="[bold green]Signed cURL[/bold green]", border_style="green"))
    console.print("[bold green]✅ Copied to clipboard![/bold green]")
