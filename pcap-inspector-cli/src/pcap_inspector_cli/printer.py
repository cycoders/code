from typing import Any, Dict, List
from rich.console import Console, ConsoleOptions
from rich.table import Table
from rich.text import Text
from rich import box


console = Console()


def print_overview(stats: Dict[str, Any], console: Console):
    overview = Text()
    overview.append(f"Packets: {stats['packets']:,} | ", style="bold")
    overview.append(f"Bytes: {stats['bytes']/1024/1024:.1f} MB | ", style="bold")
    overview.append(f"Avg Size: {stats['avg_size']:.0f} B | ", style="bold")
    overview.append(f"Duration: {stats['duration']:.1f}s", style="bold")
    console.print(overview)
    console.print()

    # Protocols
    table = Table(title="Protocol Breakdown", box=box.ROUNDED, show_header=True)
    table.add_column("Protocol", style="cyan")
    table.add_column("Packets", justify="right", style="magenta")
    table.add_column("Pct", justify="right")
    total_pkts = stats["packets"]
    for proto, count in sorted(stats["protocols"].items(), key=lambda x: x[1], reverse=True)[:15]:
        pct = count / total_pkts * 100
        name = PROTO_NAMES.get(proto, str(proto))  # Assume global PROTO_NAMES imported or copy
        table.add_row(name, f"{count:,}", f"{pct:.1f}%")
    console.print(table)

    # Top senders
    console.print("\n[bold yellow]Top Senders (Bytes)[/]")
    senders_table = Table(box=box.MINIMAL, show_header=False, expand=True)
    senders_table.add_column("IP", style="green")
    senders_table.add_column("Bytes", justify="right")
    for ip, b in sorted(stats["src_bytes"].items(), key=lambda x: x[1], reverse=True)[:10]:
        mb = b / 1024 / 1024
        senders_table.add_row(ip, f"{mb:.1f} MB")
    console.print(senders_table)

    # Top flows snippet
    flows = []  # Would compute but for overview use stats approx
    console.print("\n[bold green]Top Flows (Bytes)[/]")
    flows_table = Table(box=box.MINIMAL, expand=True)
    flows_table.add_column("Src", style="blue")
    flows_table.add_column("Dst", style="blue")
    flows_table.add_column("Proto", style="cyan")
    flows_table.add_column("Pkts", justify="right")
    flows_table.add_column("Bytes", justify="right")
    flows_table.add_column("Duration", justify="right")
    # Placeholder: in real, pass top_flows from analyzer
    # For now, skip detailed or compute small
    console.print("[dim]Run 'flows' for full table[/]")


def print_protocols(proto_stats: List[Dict], total: int, console: Console):
    table = Table(title="Protocols", box=box.ROUNDED)
    table.add_column("Protocol")
    table.add_column("Packets", justify="right")
    table.add_column("%")
    for s in proto_stats:
        table.add_row(s["proto"], str(s["packets"]), f"{s['pct']:.1f}%")
    console.print(table)


def print_talkers(data: Dict[str, List], console: Console):
    senders = data["top_senders"]
    table_s = Table(title="Top Senders", box=box.ROUNDED)
    table_s.add_column("IP")
    table_s.add_column("Bytes")
    for s in senders:
        mb = s["bytes"] / 1024 / 1024
        table_s.add_row(s["ip"], f"{mb:.1f} MB")
    console.print(table_s)

    recvs = data["top_receivers"]
    table_r = Table(title="Top Receivers", box=box.ROUNDED)
    table_r.add_column("IP")
    table_r.add_column("Bytes")
    for r in recvs:
        mb = r["bytes"] / 1024 / 1024
        table_r.add_row(r["ip"], f"{mb:.1f} MB")
    console.print(table_r)


def print_flows(flows_list: List[Dict], console: Console):
    table = Table(title="Flows", box=box.ROUNDED, expand=True)
    table.add_column("Src", style="blue")
    table.add_column("Dst", style="blue")
    table.add_column("Proto/Pkts", style="cyan")
    table.add_column("Bytes", justify="right")
    table.add_column("Duration (s)", justify="right")
    for f in flows_list:
        src = f"{f['src_ip']}:{f['src_port']}"
        dst = f"{f['dst_ip']}:{f['dst_port']}"
        proto_pkts = f"{f['proto']}/{f['packets']}"
        mb = f["bytes"] / 1024 / 1024
        table.add_row(src, dst, proto_pkts, f"{mb:.1f} MB", str(f["duration"]))
    console.print(table)


def print_packets(data: List[Dict], console: Console):
    table = Table(title="Packets", box=box.ROUNDED, expand=True)
    table.add_column("Time", style="magenta")
    table.add_column("Len", justify="right")
    table.add_column("Summary")
    table.add_column("Src")
    table.add_column("Dst")
    for d in data:
        table.add_row(
            f"{d['time']:.3f}",
            str(d["length"]),
            d["summary"][:50] + "..." if len(d["summary"]) > 50 else d["summary"],
            d["src"],
            d["dst"],
        )
    console.print(table)

# Note: PROTO_NAMES needs to be imported or defined here if used