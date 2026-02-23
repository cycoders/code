"""Main TUI application logic using Textual."""

import asyncio
from collections import defaultdict
from typing import Any, Dict, List, Optional
from docker import DockerClient
from docker.errors import DockerException, NotFound
from docker.models.containers import Container

import docker_explorer_tui
from textual.app import App, ComposeResult, on
from textual.containers import Container
from textual.events import Key
from textual.message import Message
from textual.screen import Screen, ModalScreen
from textual.split import Split
from textual.tabs import TabbedContent, TabPane
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Log,
    OptionList,
    Static,
    Tree,
)
from textual.worker import Worker
from textual.css.query import query_one


class RefreshContainers(Message):
    """Posted to refresh container list."""


class SelectContainer(Message):
    """Select a specific container."""

    def __init__(self, container_id: str, container: Container):
        super().__init__()
        self.container_id = container_id
        self.container = container


class DockerExplorerApp(App[None]):
    """Root TUI App."""

    CSS_PATH = "docker_explorer_tui.css"
    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("r", "action_refresh", "Refresh"),
        ("/", "focus_search", "Search"),
        ("?", "action_help", "Help"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.client: Optional[DockerClient] = None
        self.containers_by_id: Dict[str, Container] = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, marquee="🐳 Docker Explorer TUI")
        yield Footer()

    def on_mount(self) -> None:
        self.action_connect_docker()

    async def action_connect_docker(self) -> None:
        try:
            self.client = docker_explorer_tui.docker.from_env(timeout=5)
            await self.client.ping()
            self.notify("Connected to Docker daemon", severity="success")
            self.push_screen(ContainerListScreen(self.client))
        except Exception as error:
            self.notify(
                f"Docker connection failed: {error}\nHint: Start Docker Desktop or `sudo dockerd`",
                severity="error",
                timeout=10,
            )
            self.exit()

    def action_refresh(self) -> None:
        self.query_one(ContainerListScreen).post_message(RefreshContainers())

    def action_help(self) -> None:
        self.notify("q=quit r=refresh /=search ? =this | Esc=back", timeout=3)


class ContainerListScreen(Screen):
    """List of containers with live stats."""

    def __init__(self, client: DockerClient):
        super().__init__(title="Containers")
        self.client = client
        self.containers_by_id: Dict[str, Container] = {}

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Filter containers...", id="search-input")
        yield DataTable(
            id="containers-table",
            zebra_striped=True,
            show_cursor=True,
            expand=True,
        )

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Image", "Status", "CPU", "Mem", "Ports", "Name")
        table.column_widths = [12, 25, 12, 6, 8, 20, 20]
        self.post_message(RefreshContainers())
        self.set_interval(2.5, RefreshContainers)

    @on(RefreshContainers)
    async def on_refresh_containers(self, event: RefreshContainers) -> None:
        table: DataTable = self.query_one("#containers-table")
        search_input: Input = self.query_one("#search-input")
        filter_text = search_input.value.lower()

        table.clear(animate=False)
        self.containers_by_id.clear()

        try:
            containers = self.client.containers.list(all=True)
            for cont in containers:
                if filter_text and filter_text not in cont.name.lower() and filter_text not in cont.image.id.lower():
                    continue
                row = self._format_row(cont)
                cid_short = cont.id[:12]
                table.add_row(*row, key=cid_short)
                self.containers_by_id[cid_short] = cont
        except DockerException as e:
            self.app.notify(f"Refresh failed: {e}", severity="warning")

    def _format_row(self, cont: Container) -> List[str]:
        try:
            stats_iter = cont.stats(stream=True, decode=True)
            stats = next(stats_iter)
            cpu = f"{self._calc_cpu(stats):.1f}%"
            mem = f"{self._calc_mem(stats):.1f}%"
        except (StopIteration, Exception):
            cpu = mem = "N/A"

        ports_str = "/".join(f"{hostp}->{contp}" for hostp, contp in cont.ports.items()) or "-"
        img = cont.image.tags[0] if cont.image.tags else cont.image.id[:12]

        return [
            cont.id[:12],
            img,
            cont.status.split()[0],
            cpu,
            mem,
            ports_str,
            cont.name,
        ]

    @staticmethod
    def _calc_cpu(stats: Dict[str, Any]) -> float:
        cpu_stats = stats["cpu_stats"]["cpu_usage"]
        precpu_stats = stats["precpu_stats"]["cpu_usage"]
        cpu_delta = cpu_stats["total_usage"] - precpu_stats["total_usage"]
        system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
        num_cpus = len(cpu_stats["percpu_usage"])
        if system_delta > 0:
            return (cpu_delta / system_delta) * num_cpus * 100.0
        return 0.0

    @staticmethod
    def _calc_mem(stats: Dict[str, Any]) -> float:
        mem_stats = stats["memory_stats"]
        usage = mem_stats["usage"]
        limit = mem_stats["limit"]
        return (usage / limit * 100) if limit > 0 else 0.0

    @on(DataTable.TableRowSelected)
    def on_table_row_selected(self, event: DataTable.TableRowSelected) -> None:
        row_key = event.row_key
        if row_key and row_key in self.containers_by_id:
            cont = self.containers_by_id[row_key]
            self.app.push_screen(ContainerDetailScreen(cont, self.client))


class ContainerDetailScreen(Screen):
    """Details for a single container."""

    def __init__(self, container: Container, client: DockerClient):
        super().__init__(title=f"{container.name} ({container.id[:12]})")
        self.container = container
        self.client = client
        self.live_logs = False

    def compose(self) -> ComposeResult:
        with TabbedContent(initial="info"):
            with TabPane("Info", id="info-pane"):
                yield Static("Loading...", id="info-text")
            with TabPane("Logs", id="logs-pane"):
                yield Log(id="logs-view", auto_scroll=True)
            with TabPane("Actions"):
                yield Container(
                    Button("▶ Start", id="btn-start", variant="success"),
                    Button("⏹ Stop", id="btn-stop", variant="warning"),
                    Button("🔄 Restart", id="btn-restart"),
                    Button("💥 Kill", id="btn-kill"),
                    Button("🗑 Remove", id="btn-remove", variant="error"),
                    classes="button-bar",
                )
        yield Button("← Back", id="btn-back", variant="primary")

    def on_mount(self) -> None:
        self.load_info()
        self.load_logs()
        self.update_buttons()
        self.set_interval(1.5, self.action_update_logs)

    def load_info(self) -> None:
        attrs = self.container.attrs
        info = f"""
Name: {self.container.name}
ID: {self.container.id}
Image: {self.container.image.tags[0] if self.container.image.tags else self.container.image.id}
Status: {self.container.status}
Created: {attrs['Created']}
Ports: {dict(self.container.ports) or 'N/A'}
"""
        self.query_one(Static, "#info-text").update(info)

    def load_logs(self, clear: bool = False) -> None:
        log_view: Log = self.query_one("#logs-view")
        if clear:
            log_view.clear()
        try:
            logs_bytes = self.container.logs(tail=200, timestamps=True, stream=False)
            lines = logs_bytes.decode("utf-8", errors="replace").splitlines()
            log_view.write_lines(lines[-100:])
            log_view.scroll_end()
        except Exception as e:
            log_view.write_line(f"[error]Logs error: {e}")

    def update_buttons(self) -> None:
        status = self.container.status.split()[0].lower()
        for btn in self.query(Button):
            btn.disabled = False
        if "up" in status:
            self.query_one("#btn-start", Button).disabled = True
        else:
            self.query_one("#btn-stop", Button).disabled = True
            self.query_one("#btn-kill", Button).disabled = True

    @on(Button.Pressed, "#btn-back")
    def action_back(self) -> None:
        self.dismiss()

    @on(Button.Pressed, "#btn-start")
    async def action_start(self) -> None:
        try:
            self.container.start()
            self.notify("Container started", severity="success")
            await asyncio.sleep(0.5)
            self.container.reload()
            self.load_info()
            self.update_buttons()
        except Exception as e:
            self.notify(f"Start failed: {e}", severity="error")

    @on(Button.Pressed, "#btn-stop")
    async def action_stop(self) -> None:
        if self.app.confirm("Stop container?"):
            try:
                self.container.stop(timeout=10)
                self.notify("Container stopped")
                self.container.reload()
                self.load_info()
                self.update_buttons()
            except Exception as e:
                self.notify(f"Stop failed: {e}", severity="error")

    @on(Button.Pressed, "#btn-restart")
    async def action_restart(self) -> None:
        if self.app.confirm("Restart container?"):
            try:
                self.container.restart()
                self.notify("Container restarted")
                await asyncio.sleep(1)
                self.container.reload()
                self.load_info()
            except Exception as e:
                self.notify(f"Restart failed: {e}", severity="error")

    @on(Button.Pressed, "#btn-kill")
    async def action_kill(self) -> None:
        if self.app.confirm("Kill container (force)?"):
            try:
                self.container.kill()
                self.notify("Container killed")
                self.container.reload()
                self.load_info()
            except Exception as e:
                self.notify(f"Kill failed: {e}", severity="error")

    @on(Button.Pressed, "#btn-remove")
    async def action_remove(self) -> None:
        if self.app.confirm("Permanently remove container?"):
            try:
                self.container.remove(force=True)
                self.notify("Container removed")
                self.dismiss()
            except Exception as e:
                self.notify(f"Remove failed: {e}", severity="error")

    def action_update_logs(self) -> None:
        self.load_logs(clear=False)