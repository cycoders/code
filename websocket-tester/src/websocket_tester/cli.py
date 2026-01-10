import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

import websocket_tester
from websocket_tester.interactive import InteractiveShell
from websocket_tester.session import load_session, save_session, SessionEntry
from websocket_tester.websocket_client import WSClient

app = typer.Typer(add_completion=False)
console = Console()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)

@app.command(short_help="Interactive WebSocket shell")
def shell(
    url: Optional[str] = typer.Option(None, "--url/-u", help="Initial URL to connect"),
):
    """Launch interactive REPL shell."""
    typer.echo("WebSocket Tester v" + websocket_tester.__version__)
    shell_ = InteractiveShell(console)
    asyncio.run(shell_.run(url))

@app.command(short_help="Replay session sends to URL")
def replay(
    session_file: Path = typer.Argument(..., exists=True, help="JSONL session file"),
    url: str = typer.Option(..., "--url/-u", help="Target WS URL"),
):
    """Non-interactively replay outgoing messages from session."""
    client = WSClient(url)
    async def _replay():
        await client.connect()
        entries: list[SessionEntry] = list(load_session(session_file))
        sent = [e for e in entries if e["direction"] == "out"]
        console.print(f"[info]Replaying {len(sent)} sends...[/]")
        for entry in sent:
            payload = entry["payload"]
            msg = (
                json.dumps(payload) if isinstance(payload, dict) else str(payload)
            )
            await client.send(msg)
            console.print(f"[cyan]Replayed: {msg[:80]}{'...' if len(msg) > 80 else ''}[/] {len(msg)}B")
            await asyncio.sleep(0.05)  # Gentle throttle
        await asyncio.sleep(2)
        await client.close()
    asyncio.run(_replay())

if __name__ == "__main__":
    app()