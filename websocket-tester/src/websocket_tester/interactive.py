import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.prompt import Confirm

from .formatter import format_payload
from .session import SessionEntry, SessionManager
from .websocket_client import WSClient

logger = logging.getLogger(__name__)

class InteractiveShell:
    """Async REPL shell for WS interaction."""

    COMMANDS = {
        "connect",
        "send",
        "disconnect",
        "replay",
        "save",
        "load",
        "clear",
        "help",
        "quit",
        "exit",
        "q",
    }

    def __init__(self, console: Console):
        self.console = console
        self.client: Optional[WSClient] = None
        self.recv_task: Optional[asyncio.Task] = None
        self.session_entries: list[SessionEntry] = []
        self.prompt = PromptSession(
            history=FileHistory("~/.ws-tester-history"),
            completer=WordCompleter(list(self.COMMANDS), ignore_case=True),
            style=Style.from_dict({"prompt": "bold green"}),
        )

    async def run(self, initial_url: Optional[str] = None) -> None:
        """Main REPL loop."""
        self.print_help()
        if initial_url:
            await self.cmd_connect(initial_url)
        try:
            while True:
                line = await asyncio.get_running_loop().run_in_executor(
                    None, lambda: self.prompt.prompt_async("> ")
                )
                await self.process_line(line.strip())
        except KeyboardInterrupt:
            if Confirm.ask("[yellow]Quit?[/]"):
                await self.shutdown()
        except EOFError:
            await self.shutdown()

    async def process_line(self, line: str) -> None:
        if not line or line.startswith("#"):
            return
        parts = line.split(maxsplit=1)
        cmd, *args = parts
        cmd = cmd.lower()
        arg_str = parts[1] if len(parts) > 1 else ""
        {
            "connect": self.cmd_connect,
            "send": self.cmd_send,
            "disconnect": self.cmd_disconnect,
            "replay": self.cmd_replay,
            "save": self.cmd_save,
            "load": self.cmd_load,
            "clear": self.cmd_clear,
            "help": self.print_help,
            "quit": self.shutdown,
            "exit": self.shutdown,
            "q": self.shutdown,
        }.get(cmd, self.cmd_unknown)(arg_str)

    async def cmd_connect(self, uri: str) -> None:
        await self.cmd_disconnect()  # Close existing
        try:
            self.client = WSClient(uri.strip())
            await self.client.connect()
            self.console.print(f"[bold green]Connected: {uri}[/] 🎉")
            self.recv_task = asyncio.create_task(self._recv_loop())
        except Exception as e:
            self.console.print(f"[bold red]Connect failed: {e}[/] 💥")

    async def cmd_send(self, raw: str) -> None:
        if not self.client or not self.client.connected:
            self.console.print("[red]Connect first![/]")
            return
        if not raw:
            raw = self.console.input("[dim]Message[/dim] > ")
        msg = self._parse_message(raw)
        ts = datetime.now().isoformat()
        entry = SessionManager.new_entry("out", msg, ts)
        self.session_entries.append(entry)
        self.console.print("[bold cyan]OUT:[/]", end="")
        format_payload(msg)
        await self.client.send(msg)

    async def cmd_disconnect(self, *_: str) -> None:
        if self.recv_task:
            self.recv_task.cancel()
            try:
                await self.recv_task
            except asyncio.CancelledError:
                pass
        if self.client:
            await self.client.close()
            self.client = None
        self.console.print("[yellow]Disconnected[/]")

    async def cmd_replay(self, path_str: str) -> None:
        if not self.client:
            self.console.print("[red]Connect first![/]")
            return
        path = Path(path_str)
        try:
            entries = list(load_session(path))  # from session
            sent = [e for e in entries if e["direction"] == "out"]
            self.console.print(f"[info]Replaying {len(sent)} messages[/]")
            for entry in sent:
                msg = (
                    json.dumps(entry["payload"])
                    if isinstance(entry["payload"], dict)
                    else str(entry["payload"])
                )
                self.console.print("[cyan]REPLAY OUT:[/]", end="")
                format_payload(msg)
                await self.client.send(msg)
                await asyncio.sleep(0.1)
        except Exception as e:
            self.console.print(f"[red]Replay error: {e}[/]")

    async def cmd_save(self, path_str: str) -> None:
        if not path_str:
            path_str = str(Path("session.jsonl"))
        path = Path(path_str)
        SessionManager.save(self.session_entries, path)
        self.console.print(f"[green]Saved {len(self.session_entries)} entries to {path}[/] 💾")

    async def cmd_load(self, path_str: str) -> None:
        path = Path(path_str or "session.jsonl")
        try:
            new_entries = list(load_session(path))
            self.session_entries.extend(new_entries)
            self.console.print(f"[green]Loaded {len(new_entries)} entries (total: {len(self.session_entries)})[/] 📂")
        except Exception as e:
            self.console.print(f"[red]Load error: {e}[/]")

    async def cmd_clear(self, *_: str) -> None:
        self.console.clear()
        self.print_help()

    def cmd_unknown(self, cmd: str) -> None:
        self.console.print(f"[red]Unknown: {cmd}. Type /help[/red]")

    async def _recv_loop(self) -> None:
        while self.client and self.client.connected:
            msg = await self.client.recv()
            if msg:
                ts = datetime.now().isoformat()
                entry = SessionManager.new_entry("in", msg, ts)
                self.session_entries.append(entry)
                self.console.print("[bold green]IN:[/]", end="")
                format_payload(msg)
            else:
                await asyncio.sleep(0.01)

    def print_help(self) -> None:
        help_text = """
[bold]Commands:[/]
  /connect <ws://url>    Connect (or --url flag)
  /send <json/text/@file> Send message
  /replay <session.jsonl> Replay outs
  /save [file.jsonl]     Save session
  /load <file.jsonl>     Append session
  /disconnect            Close WS
  /clear                 Clear screen
  /help /?               This help
  /quit /exit /q         Exit

[bold green]Tip:[/] Tab for complete, ↑↓ history. Ctrl+C safe quit.[/]
        """
        self.console.print(help_text)

    async def shutdown(self, *_: str) -> None:
        """Clean shutdown."""
        await self.cmd_disconnect()
        sys.exit(0)

    @staticmethod
    def _parse_message(raw: str) -> str:
        """Parse raw to sendable str (JSON/file/raw)."""
        raw = raw.strip()
        if raw.startswith("@"):
            return Path(raw[1:]).read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
            return json.dumps(data)
        except json.JSONDecodeError:
            return raw