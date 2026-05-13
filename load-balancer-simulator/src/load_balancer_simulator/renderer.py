from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel


def render_results(results: Dict[str, Any], console: Console):
    table = Table(title="Load Balancer Results")
    table.add_column("Backend", style="cyan")
    table.add_column("Reqs")
    table.add_column("Errors")
    table.add_column("p95 Lat (s)")
    table.add_column("Max QLen")
    table.add_column("Util %")

    for bname, bstats in results['backends'].items():
        table.add_row(
            bname,
            str(bstats['total_reqs']),
            str(bstats['errors']),
            f"{bstats.get('p95', 0):.3f}",
            str(bstats['max_queue_len']),
            f"{bstats.get('utilization', 0)*100:.0f}%",
        )

    console.print(table)

    g = results['global']
    console.print(
        Panel.fitt(
            f"[bold]Global:[/bold] p95={g['p95']:.3f}s, Error={g['error_rate']*100:.1f}%, Throughput={g['throughput']:.0f} rps",
            title="Summary"
        )
    )


def render_live(results: Dict[str, Any]):
    console = Console()

    def make_table():
        table = Table.grid(expand=True)
        table.add_column("Backend", style="bold magenta")
        table.add_column("Queue")
        table.add_column("Active")
        table.add_column("Util %")
        table.add_column("p95 (s)")

        # Use last live_data for demo
        if results['live_data']:
            snapshot = results['live_data'][-1]
            for bname in snapshot['qlens']:
                qlen = snapshot['qlens'][bname]
                active = snapshot['actives'][bname]
                util = snapshot['util'][bname] * 100
                p95 = 0.1  # placeholder
                table.add_row(bname, str(qlen), str(active), f"{util:.0f}%", f"{p95:.2f}")

        summary = f"Time: {snapshot['time']:.1f}s | Processed: {snapshot['processed']}"
        return Panel(table, title=summary)

    with Live(make_table(), refresh_per_second=4, console=console) as live:
        # Simulate live by sleeping, but since sim done, show final
        time.sleep(2)
