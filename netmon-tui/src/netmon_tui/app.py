import asyncio
import json
import logging
import os

from pathlib import Path

from typing import Any

import psutil

from textual.app import App, ComposeResult, on
from textual.binding import Binding
from textual.message import Message
from textual.widgets import DataTable, Footer, Header, Horizontal, Input, Label
from textual.widgets._data_table import RowKey
from textual import events, log

from .fetchers import get_connections, get_interface_stats
from .models import Connection


log = logging.getLogger(__name__)


class DataUpdate(Message, bubble=False):
    """Emitted when fresh data is loaded."""


class NetmonApp(App):
    """Main TUI application."""

    CSS = """
    DataTable {
        height: 1fr;
        max-height: 0fr;
    }
    #filter_row {
        Column {
            width: 1fr;
        }
        Input {
            margin: 0 1;
            width: 1fr;
        }
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "request_refresh", "Refresh"),
        Binding("f", "focus_filter", "Filter"),
        Binding("e", "export_data", "Export"),
    ]

    def __init__(self, refresh_interval: float = 1.0) -> None:
        self.refresh_interval = max(0.1, refresh_interval)
        self.connections: list[Connection] = []
        self.interfaces: dict[str, dict[str, int]] = {}
        self.prev_counters: dict[str, dict[str, int]] = {}
        self.filter_str = ""
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, marquee="Netmon TUI")
        yield DataTable("Interface", "↑ TX/s", "↓ RX/s", "Total ↑", "Total ↓", id="if_table")
        yield Horizontal(
            Label("Filter:", id="filter_label"),
            Input(placeholder="live filter conns...", id="filter_input"),
            id="filter_row",
        )
        yield DataTable(
            "Local", "Remote", "Status", "PID", "Process",
            id="conn_table",
        )
        yield Footer(help_text="q:quit | r:refresh | f:filter | e:export")

    def on_mount(self) -> None:
        if_table: DataTable = self.query_one("#if_table", DataTable)
        conn_table: DataTable = self.query_one("#conn_table", DataTable)

        if_table.zebra_stripes = True
        if_table.add_row("-", "-", "-", "-", "-")  # header stripe

        conn_table.zebra_stripes = True
        conn_table.cursor_type = "row"

        # Initial load + interval
        self.action_request_refresh()
        self.set_interval(self.refresh_interval, self.action_request_refresh)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Live filter on input change."""
        self.filter_str = event.value.lower()
        self.update_conn_table()

    async def action_request_refresh(self) -> None:
        """Async refresh data."""
        try:
            self.connections = await get_connections()
            self.interfaces = await get_interface_stats()
            self.post_message(DataUpdate())
        except Exception as error:
            self.notify(f"Fetch error: {error}", severity="error", timeout=3.0)

    def on_data_update(self, event: DataUpdate) -> None:
        """Update both tables on new data."""
        self.update_if_table()
        self.update_conn_table()

    def update_if_table(self) -> None:
        """Update interface table with rates/deltas."""
        table: DataTable = self.query_one("#if_table")
        table.clear(animate=False)

        for name, io in self.interfaces.items():
            prev = self.prev_counters.get(name, {"bytes_sent": 0, "bytes_recv": 0})
            sent_delta = io["bytes_sent"] - prev["bytes_sent"]
            recv_delta = io["bytes_recv"] - prev["bytes_recv"]
            tx_rate = sent_delta / 1024 / 1024 / self.refresh_interval
            rx_rate = recv_delta / 1024 / 1024 / self.refresh_interval
            total_tx_gb = io["bytes_sent"] / 1024 / 1024 / 1024
            total_rx_gb = io["bytes_recv"] / 1024 / 1024 / 1024

            table.add_row(
                name,
                f"{tx_rate:.2f}",
                f"{rx_rate:.2f}",
                f"{total_tx_gb:.1f}G",
                f"{total_rx_gb:.1f}G",
            )

        self.prev_counters = {n: io for n, io in self.interfaces.items()}

    def update_conn_table(self) -> None:
        """Update connections table with filter/sort."""
        table: DataTable = self.query_one("#conn_table")
        table.clear(animate=False)

        displayed = 0
        for conn in self.connections:
            conn_str = str(conn).lower()
            if self.filter_str and self.filter_str not in conn_str:
                continue

            lstr = f"{conn.local.ip}:{conn.local.port}"
            rstr = f"{conn.raddr.ip}:{conn.raddr.port or ''}"
            pidstr = str(conn.pid) if conn.pid else "-"
            procstr = conn.process_name or "kernel/-"

            table.add_row(lstr, rstr, conn.status, pidstr, procstr)
            displayed += 1
            if displayed > 500:  # perf cap
                break

        table.label = f"Connections (filtered: {self.filter_str or 'all'}, showing {displayed})"

    def action_focus_filter(self) -> None:
        """Focus filter input."""
        self.query_one("#filter_input", Input).focus()

    def action_export_data(self) -> None:
        """Export visible connections to JSON."""
        export_path = Path("netmon-export.json")
        try:
            data = [{
                "local": conn.local._asdict(),
                "raddr": conn.raddr._asdict(),
                "status": conn.status,
                "pid": conn.pid,
                "process": conn.process_name,
            } for conn in self.connections]
            export_path.write_text(json.dumps(data, indent=2))
            self.notify(f"Exported {len(data)} conns to {export_path}", severity="success")
        except Exception as e:
            self.notify(f"Export failed: {e}", severity="error")
