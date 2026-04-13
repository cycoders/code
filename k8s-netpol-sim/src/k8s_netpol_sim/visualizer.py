from typing import Dict, Any, Tuple

import rich

import k8s_netpol_sim.models as m


console = rich.console.Console()
table = rich.table.Table


def print_result(allowed: bool, details: Dict[str, Any]) -> None:
    """Print rich summary table."""
    status_emoji = "✅" if allowed else "❌"
    flow = f"[bold cyan]{details['src']}[/bold cyan] → [bold cyan]{details['dst']}[/bold cyan]:[bold magenta]{details['port_protocol']}[/bold magenta]"

    console.print(f"\n[bold]{status_emoji} Allowed:[/bold] {flow}")

    t = table(title="Policy Details", expand=True)
    t.add_column("Direction", style="cyan")
    t.add_column("Status", style="green" if allowed else "red")
    t.add_column("Allowing Policies", style="green")
    t.add_column("Blocking Policies", style="red")

    for dir_name, dir_details in (("Egress", details["egress"]), ("Ingress", details["ingress"])):
        status = "✅ Allowed" if dir_details["blocking"] else "❌ Blocked"
        allowing = ", ".join(dir_details["allowing"]) or "(default)"
        blocking = ", ".join(dir_details["blocking"]) or "none"
        t.add_row(
            dir_name,
            status,
            allowing,
            blocking,
        )
    console.print(t)


def mermaid_graph(details: Dict[str, Any], allowed: bool) -> str:
    """Generate Mermaid diagram for flow."""
    color = "green" if allowed else "red"
    label = "✅ allowed" if allowed else "❌ blocked"
    src = details["src"].replace("/", "\\n")
    dst = details["dst"].replace("/", "\\n")
    port = details["port_protocol"]
    return f"""```mermaid
graph LR
    A["{src}"] -->|TCP/{port} {label}| B["{dst}"]
    classDef {color} fill:{color},stroke:#333,stroke-width:2px
    class A,B {color}
```"""

console.print(mermaid_graph(details, allowed))