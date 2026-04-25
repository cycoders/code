import time
import random
import math
from typing import List, Dict
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich.text import Text
from .models import SimulationConfig, BreakerConfig
from .breaker import create_breaker, Breaker
from .stats import SimulationStats, BreakerStats

class Simulator:
    def __init__(self, config: SimulationConfig, console: Console = None):
        self.config = config
        self.console = console or Console()
        self.breakers: List[Breaker] = [create_breaker(b.name, b) for b in config.breakers]
        self.stats = SimulationStats()
        for b in self.breakers:
            self.stats.breakers[b.name] = BreakerStats()

    def run(self, output: str = "console") -> SimulationStats:
        """Run simulation, return stats."""
        virtual_time = 0.0
        req_count = 0
        open_start = {b.name: 0.0 for b in self.breakers}
        prev_time = 0.0
        latencies = []

        table = self._build_table()
        with Live(table, console=self.console, refresh_per_second=10, screen=True) as live:
            while virtual_time < self.config.duration_secs:
                # Poisson next req time
                rate = self.config.rps
                if self.config.ramp_duration_secs > 0:
                    progress = min(virtual_time / self.config.ramp_duration_secs, 1.0)
                    rate = self.config.rps * progress
                interval = random.expovariate(rate)
                virtual_time += interval
                if virtual_time > self.config.duration_secs:
                    break

                # Pick random breaker
                breaker = random.choice(self.breakers)
                bname = breaker.name
                self.stats.breakers[bname].total_requests += 1
                req_count += 1

                if breaker.allow():
                    # Simulate service
                    service_success = random.random() > self.config.error_rate
                    breaker.on_result(service_success)
                    self.stats.breakers[bname].service_calls += 1
                    latency = 50 + random.expovariate(1/20) * 10  # mean 50ms, var
                    latencies.append(latency)
                    if service_success:
                        self.stats.breakers[bname].successes += 1
                        self.stats.record_latency(bname, latency)
                    else:
                        self.stats.breakers[bname].service_failures += 1
                else:
                    self.stats.breakers[bname].rejects += 1

                # Update open durations every sec
                if int(virtual_time) > int(prev_time):
                    for b in self.breakers:
                        if b.state == b.OPEN:
                            open_start[b.name] = virtual_time  # simplistic
                        else:
                            if open_start[b.name] > 0:
                                self.stats.add_open_duration(b.name, virtual_time - open_start[b.name])
                                open_start[b.name] = 0
                    prev_time = int(virtual_time)

                # Update live table
                self._update_table(table)
                live.update(table)

        # Final open durations
        for bname in open_start:
            if open_start[bname] > 0:
                self.stats.add_open_duration(bname, self.config.duration_secs - open_start[bname])

        if output == "json":
            import json
            print(json.dumps(self.stats.to_dict(), indent=2))
        elif output == "csv":
            self._print_csv()
        else:
            self._print_final_table()

        return self.stats

    def _build_table(self) -> Table:
        table = Table(title="Circuit Breaker Simulation Live", show_header=True)
        table.add_column("Breaker", style="cyan")
        table.add_column("State", style="magenta")
        table.add_column("Reqs", justify="right")
        table.add_column("Rejects", justify="right")
        table.add_column("Reject %", justify="right")
        table.add_column("Open (s)", justify="right")
        table.add_column("Avg Lat (ms)", justify="right")
        return table

    def _update_table(self, table: Table):
        table.rows.clear()
        for breaker in self.breakers:
            stats = self.stats.breakers[breaker.name]
            open_secs = sum(stats.open_durations)
            table.add_row(
                breaker.name,
                str(breaker.state),
                str(stats.total_requests),
                str(stats.rejects),
                f"{stats.reject_rate:.1f}%",
                f"{open_secs:.0f}",
                f"{stats.avg_latency:.0f}" if stats.latencies else "N/A",
            )

    def _print_final_table(self):
        self.console.print("\n[bold green]Simulation Complete[/]")
        table = self._build_table()
        self._update_table(table)
        self.console.print(table)

    def _print_csv(self):
        import csv
        import sys
        writer = csv.DictWriter(sys.stdout, fieldnames=["breaker"] + list(self.stats.breakers["default"].to_dict().keys()))
        writer.writeheader()
        for name, s in self.stats.to_dict().items():
            row = {"breaker": name, **s}
            writer.writerow(row)
