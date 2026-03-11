from typing import Dict, Any
from textual.app import App, ComposeResult
from textual.widgets import (
    Header,
    Footer,
    Select,
    Input,
    Button,
    Static,
    DataTable,
)
from textual.containers import Container
from textual.message import Message
from textual.worker import await_worker
from textual import work

from .simulator import SimulationConfig, run_simulation, Stats
from .policies import create_policy


class StatsUpdate(Message):
    stats: Stats


POLICY_OPTIONS = [
    ("Fixed Window", "fixed"),
    ("Sliding Window", "sliding"),
    ("Token Bucket", "token"),
    ("Leaky Bucket", "leaky"),
]


class RateLimitApp(App):
    CSS = """
    Screen {
        layout: horizontal;
    }
    #controls {
        layout: vertical;
        padding: 1;
        height: 1fr;
    }
    #graph {
        height: 10;
        content-align: center middle;
        background: $panel;
    }
    #stats {
        height: 1fr;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stats: Stats | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="sidebar"):
            yield Select(POLICY_OPTIONS, id="policy", value="token")
            yield Input("100", placeholder="Limit/Capacity", id="limit")
            yield Input("60", placeholder="Window (s)" , id="window")
            yield Input("1.67", placeholder="Refill/Leak Rate (req/s)", id="refill")
            yield Input("10", placeholder="RPS", id="rps")
            yield Input("60", placeholder="Duration (s)", id="duration")
            yield Input("5", placeholder="Num Users", id="users")
            yield Button("Simulate", id="simulate", variant="primary")
        yield Static(id="graph")
        yield DataTable(id="stats", zebra_stripes=True)
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "simulate":
            self.action_simulate()

    @work(exclusive=True)
    async def action_simulate(self) -> None:
        try:
            policy_name = self.query_one(Select, "#policy").value
            limit = int(self.query_one("#limit", Input).value or 100)
            window = float(self.query_one("#window", Input).value or 60)
            refill = float(self.query_one("#refill", Input).value or limit / window)
            rps = float(self.query_one("#rps", Input).value or 10)
            duration = float(self.query_one("#duration", Input).value or 60)
            num_keys = int(self.query_one("#users", Input).value or 5)

            params: Dict[str, Any] = {"limit": limit, "window": window}
            p_lower = policy_name.lower()
            if "token" in p_lower:
                params = {"capacity": float(limit), "refill_rate": refill}
            elif "leaky" in p_lower:
                params = {"capacity": limit, "leak_rate": refill}

            config = SimulationConfig(
                duration=duration,
                rps=rps,
                num_keys=num_keys,
                policy_name=p_lower,
                policy_params=params,
            )
            stats = run_simulation(config)
            self.post_message(StatsUpdate(stats))
        except ValueError as e:
            self.notify(f"Invalid input: {e}", severity="error")

    async def on_stats_update(self, message: StatsUpdate) -> None:
        self.stats = message.stats
        await self.update_ui()

    async def update_ui(self) -> None:
        if not self.stats:
            return
        s = self.stats

        # Sparkline
        accepts = [1 if d else 0 for d in s.decisions]
        from .utils import render_sparkline
        spark = render_sparkline(accepts, width=100)
        self.query_one("#graph", Static).update(spark)

        # Table
        table = self.query_one("#stats", DataTable)
        table.clear(columns=True)
        table.add_columns("Metric", "Value")
        table.add_row("Hit Rate", f"{s.hit_rate:.1%}")
        table.add_row("Total Requests", str(s.total_requests))
        table.add_row("Accepted", str(s.accepted))
        table.add_row("Rejected", str(s.rejected))
        table.add_row("Max Burst", str(s.max_burst))
