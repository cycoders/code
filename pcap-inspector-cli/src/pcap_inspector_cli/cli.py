import typer
from pathlib import Path
import json
from typing import Optional

from rich.console import Console

from .analyzer import Analyzer
from .printer import print_overview, print_protocols, print_talkers, print_flows, print_packets


app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()


@app.command(help="Show overview stats protocols talkers and top flows")
def inspect(
    file_path: Path = typer.Argument(..., exists=True, help="Path to PCAP file"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    try:
        analyzer = Analyzer(file_path)
        stats = analyzer.get_stats()
        if json_output:
            print(json.dumps(stats, indent=2))
        else:
            print_overview(stats, console)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command(help="Protocol breakdown table")
def protocols(
    file_path: Path = typer.Argument(..., exists=True),
    json_output: bool = typer.Option(False, "--json"),
):
    analyzer = Analyzer(file_path)
    stats = analyzer.get_stats()
    proto_stats = [
        {"proto": k, "packets": v, "pct": round(v / stats["packets"] * 100, 1)}
        for k, v in stats["protocols"].most_common()
    ]
    if json_output:
        print(json.dumps(proto_stats, indent=2))
    else:
        print_protocols(proto_stats, stats["packets"], console)


@app.command(help="Top IP talkers senders and receivers")
def talkers(
    file_path: Path = typer.Argument(..., exists=True),
    top_n: int = typer.Option(10, "--top", min=1, max=50),
    json_output: bool = typer.Option(False, "--json"),
):
    analyzer = Analyzer(file_path)
    stats = analyzer.get_stats()
    senders = [
        {"ip": ip, "bytes": stats["src_bytes"][ip]}
        for ip in sorted(stats["src_bytes"], key=stats["src_bytes"].get, reverse=True)[:top_n]
    ]
    receivers = [
        {"ip": ip, "bytes": stats["dst_bytes"][ip]}
        for ip in sorted(stats["dst_bytes"], key=stats["dst_bytes"].get, reverse=True)[:top_n]
    ]
    data = {"top_senders": senders, "top_receivers": receivers}
    if json_output:
        print(json.dumps(data, indent=2))
    else:
        print_talkers(data, console)


@app.command(help="Conversation flows sorted by bytes")
def flows(
    file_path: Path = typer.Argument(..., exists=True),
    top_n: int = typer.Option(10, "--top", min=1, max=100),
    json_output: bool = typer.Option(False, "--json"),
):
    analyzer = Analyzer(file_path)
    flows_list = analyzer.get_flows(top_n)
    if json_output:
        print(json.dumps(flows_list, indent=2))
    else:
        print_flows(flows_list, console)


@app.command(help="List packets with optional BPF filter")
def packets(
    file_path: Path = typer.Argument(..., exists=True),
    filter_str: Optional[str] = typer.Option(None, "--filter", help="BPF filter e.g. tcp port 80"),
    limit: int = typer.Option(100, "--limit", min=1, max=10000),
    json_output: bool = typer.Option(False, "--json"),
):
    from scapy.all import sniff
    kwargs = {"offline": str(file_path), "store": True, "count": limit}
    if filter_str:
        kwargs["filter"] = filter_str
    pkts = sniff(**kwargs)
    data = []
    for p in pkts:
        summary = p.summary()
        src = dst = "-"
        if hasattr(p, "src"):
            src = p.src
        if hasattr(p, "dst"):
            dst = p.dst
        data.append({
            "time": float(p.time),
            "length": len(p),
            "summary": summary,
            "src": src,
            "dst": dst,
        })
    if json_output:
        print(json.dumps(data, indent=2))
    else:
        print_packets(data, console)


@app.command(help="Export filtered data to JSON CSV or PCAP")
def export(
    file_path: Path = typer.Argument(..., exists=True),
    fmt: str = typer.Argument("json", choices=["json", "csv", "pcap"]),
    output: Path = typer.Option(Path("-"), "--output", help="Output file (- for stdout)"),
    filter_str: Optional[str] = typer.Option(None, "--filter"),
):
    from scapy.all import sniff, wrpcap
    import csv
    kwargs = {"offline": str(file_path)}
    if filter_str:
        kwargs["filter"] = filter_str
    pkts = sniff(**kwargs, store=True)
    if fmt == "pcap":
        outpath = str(output) if output != Path("-") else "output.pcap"
        wrpcap(outpath, pkts)
        typer.echo(f"Exported {len(pkts)} packets to {outpath}")
        return
    # JSON/CSV data
    data = []
    for p in pkts:
        src = p.src if hasattr(p, "src") else ""
        dst = p.dst if hasattr(p, "dst") else ""
        data.append({
            "time": float(p.time),
            "length": len(p),
            "src": src,
            "dst": dst,
            "summary": p.summary(),
        })
    if fmt == "json":
        outstr = json.dumps(data, indent=2)
    else:  # csv
        if output != Path("-"):
            with open(output, "w") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            typer.echo(f"Exported to {output}")
            return
        else:
            import io
            outstr = io.StringIO()
            writer = csv.DictWriter(outstr, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            outstr.seek(0)
            outstr = outstr.getvalue()
    if output == Path("-"):
        print(outstr)
    else:
        output.write_text(outstr)
        typer.echo(f"Exported to {output}")


if __name__ == "__main__":
    app()