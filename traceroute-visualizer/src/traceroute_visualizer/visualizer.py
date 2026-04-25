import statistics
from pathlib import Path
from typing import List
import re
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from .models import Hop

COUNTRY_FLAGS = {
    'us': '🇺🇸', 'gb': '🇬🇧', 'de': '🇩🇪', 'fr': '🇫🇷', 'cn': '🇨🇳', 'jp': '🇯🇵',
    'au': '🇦🇺', 'ca': '🇨🇦', 'in': '🇮🇳', 'br': '🇧🇷', 'ru': '🇷🇺', 'kr': '🇰🇷',
    'it': '🇮🇹', 'es': '🇪🇸', 'nl': '🇳🇱', 'se': '🇸🇪', 'no': '🇳🇴', 'ch': '🇨🇭',
    'mx': '🇲🇽', 'ar': '🇦🇷'
}

console = Console()


def print_table(hops: List[Hop]) -> None:
    table = Table(expand=True, show_header=True, header_style="bold magenta")
    table.add_column("Hop", style="cyan", no_wrap=True)
    table.add_column("IP", style="green")
    table.add_column("Avg RTT", justify="right")
    table.add_column("Loss %", justify="right")
    table.add_column("Jitter", justify="right")
    table.add_column("ASN")
    table.add_column("Org")
    table.add_column("Country")

    max_rtt = max((statistics.mean([r for r in h.rtts if r < float('inf')]) for h in hops if any(r < float('inf') for r in h.rtts)), default=0)
    total_loss = sum(len([r for r in h.rtts if r == float('inf')]) / len(h.rtts) for h in hops) / len(hops) * 100

    summary = f"Hops: {len(hops)}  Max RTT: {max_rtt:.1f}ms  Avg Loss: {total_loss:.0f}%"
    console.print(Panel(table, title="[bold blue]Traceroute Path", subtitle=summary))

    for h in hops:
        finite_rtts = [r for r in h.rtts if r < float('inf')]
        avg = statistics.mean(finite_rtts) if finite_rtts else float('inf')
        loss_pct = len([r for r in h.rtts if r == float('inf')]) / len(h.rtts) * 100
        jitter = statistics.stdev(finite_rtts) if len(finite_rtts) > 1 else 0.0
        flag = COUNTRY_FLAGS.get(h.country.lower(), '❓') if h.country else '─'
        avg_str = f"{avg:.1f}ms" if avg < float('inf') else "timeout"
        table.add_row(
            str(h.hop_num),
            h.ip,
            avg_str,
            f"{loss_pct:.0f}%",
            f"{jitter:.1f}",
            h.asn or "─",
            h.org or "─",
            flag
        )
    console.print(table)


def print_histogram(hops: List[Hop]) -> None:
    finite_rtts = [r for h in hops for r in h.rtts if r < float('inf')]
    if not finite_rtts:
        return
    min_rtt, max_rtt = min(finite_rtts), max(finite_rtts)
    if max_rtt - min_rtt < 1:
        return
    num_bins = 10
    bin_width = (max_rtt - min_rtt) / num_bins
    hist = [0] * num_bins
    for rtt in finite_rtts:
        bin_idx = min(int((rtt - min_rtt) / bin_width), num_bins - 1)
        hist[bin_idx] += 1
    max_count = max(hist)
    lines = []
    for i in range(num_bins):
        bar_len = int((hist[i] / max_count) * 50) if max_count > 0 else 0
        bar = '█' * bar_len
        label = f"{min_rtt + i*bin_width:.0f}-{min_rtt + (i+1)*bin_width:.0f}"
        lines.append(f"{label}: {bar} {hist[i]}")
    console.print(Panel("\n".join(lines), title="[bold green]RTT Histogram (ms)"))


def generate_svg(hops: List[Hop], output_path: Path) -> None:
    width, height = 1200, 200
    x_step = max(1100 / max(len(hops), 10), 40)
    svg_content = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="100%" height="100%" fill="#f8f9fa"/>',
    ]
    # Lines
    for i in range(1, len(hops)):
        x1 = 50 + (i-1) * x_step
        x2 = 50 + i * x_step
        svg_content.append(f'<line x1="{x1}" y1="100" x2="{x2}" y2="100" stroke="#007bff" stroke-width="3" stroke-linecap="round"/>')
    # Nodes
    for i, hop in enumerate(hops):
        x = 50 + i * x_step
        finite_rtts = [r for r in hop.rtts if r < float('inf')]
        avg = statistics.mean(finite_rtts) if finite_rtts else float('inf')
        if avg < 50:
            fill = "#28a745"
        elif avg < 200:
            fill = "#ffc107"
        else:
            fill = "#dc3545"
        svg_content.append(f'<circle cx="{x}" cy="100" r="18" fill="{fill}" stroke="#343a40" stroke-width="2"/>')
        svg_content.append(f'<text x="{x}" y="95" text-anchor="middle" font-weight="bold" font-size="14">{hop.hop_num}</text>')
        svg_content.append(f'<text x="{x}" y="122" text-anchor="middle" font-size="10">{hop.ip[:12]}...</text>')
        if hop.asn:
            svg_content.append(f'<text x="{x}" y="138" text-anchor="middle" font-size="9" fill="#6c757d">{hop.asn}</text>')
    svg_content.append('</svg>')
    output_path.write_text("\n".join(svg_content))
    console.print(f"[green]SVG saved: {output_path}")