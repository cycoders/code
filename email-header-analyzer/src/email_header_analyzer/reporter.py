from typing import Dict, Any, List
from rich.console import Console, RenderableType
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich import box

STATUS_EMOJI = {
    "pass": "🟢",
    "fail": "🔴",
    "softfail": "🟡",
    "neutral": "⚪",
    "none": "⚪",
    "unknown": "⚪",
    "permerror": "🟠",
    "temperror": "🟠",
    "error": "🔴",
    "timeout": "⏳",
}

def generate_report(console: Console, analysis: Dict[str, Any], verbose: bool) -> None:
    console.print(Panel("📧 Email Deliverability Report", style="bold cyan"))

    # Summary Table
    table = Table(title="Summary", box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="green")

    dkim_stat = analysis["dkim"][0]["result"] if analysis["dkim"] else "unknown"
    spf_stat = analysis["spf"]["status"]
    dmarc_stat = analysis["dmarc"]["status"]

    table.add_row("DKIM", f"{STATUS_EMOJI.get(dkim_stat, '❓')} {dkim_stat.title()}")
    table.add_row("SPF", f"{STATUS_EMOJI.get(spf_stat, '❓')} {spf_stat.title()}")
    table.add_row("DMARC", f"{STATUS_EMOJI.get(dmarc_stat, '❓')} {dmarc_stat.title()}")
    console.print(table)

    # Received Chain Tree
    tree = Tree("📨 Delivery Path (sender → receiver)", guide_style="green")
    for hop in analysis["received"]:
        label = f"{STATUS_EMOJI.get('neutral', '⚪')} {hop['ip']} from [blue]{hop['helo']}"
        tree.add(label)
    console.print(tree)

    if verbose:
        _verbose_details(console, analysis)

    # Quick tips
    tips = _get_tips(analysis)
    console.print(Panel("\n".join(tips), title="🔧 Fixes", border_style="yellow"))

def _verbose_details(console: Console, analysis: Dict[str, Any]) -> None:
    # DKIM table
    if analysis["dkim"]:
        dtable = Table(title="DKIM Signatures")
        dtable.add_column("Selector")
        dtable.add_column("Domain")
        dtable.add_column("Result")
        for sig in analysis["dkim"]:
            status = STATUS_EMOJI.get(sig.get("result", ""), "❓")
            dtable.add_row(
                sig.get("selector", ""),
                sig.get("domain", ""),
                f"{status} {sig.get('result', '')}",
            )
        console.print(dtable)

    # SPF
    spf = analysis["spf"]
    console.print(f"\nSPF Record: [italic]{spf.get('record', 'N/A')}[/]")


def _get_tips(analysis: Dict[str, Any]) -> List[str]:
    tips = []
    if analysis["spf"]["status"] != "pass":
        tips.append("• Add SPF TXT: v=spf1 ip4:YOUR.IP include:_spf.google.com ~all")
    if not analysis["dkim"]:
        tips.append("• Set up DKIM: Generate keys, add sig to outgoing mail")
    if analysis["dmarc"]["status"] == "reject":
        tips.append("• DMARC p=reject: Fix auth before sending")
    return tips if tips else ["✅ Looks good!"]
