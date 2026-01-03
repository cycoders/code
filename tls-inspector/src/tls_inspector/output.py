from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from tls_inspector.models import TLSReport


console = Console()


def render_report(report: TLSReport) -> None:
    """Render beautiful report using Rich."""
    console.print(Panel(
        f"[bold cyan]{report.host}:{report.port}[/]",
        title="[bold cyan]TLS Inspector Report[/]",
        box=box.ROUNDED
    ))

    # Protocols table
    proto_table = Table(title="[cyan]Supported Protocols[/]", expand=True)
    proto_table.add_column("Protocol", style="cyan")
    proto_table.add_column("Status", style="green")
    for proto in ["TLS 1.3", "TLS 1.2", "TLS 1.1", "TLS 1.0"]:
        status = "[green]✓[/]" if proto in report.protocols else "[red]✗[/]"
        proto_table.add_row(proto, status)
    console.print(proto_table)

    # Negotiated
    console.print(
        f"[bold]Negotiated:[/] [magenta]{report.negotiated_protocol}[/] / [yellow]{report.negotiated_cipher}[/]"
    )

    # Supported ciphers
    if report.supported_ciphers:
        top_ciphers = report.supported_ciphers[:8]
        console.print(f"[bold]Top Ciphers:[/] {', '.join(top_ciphers)}")

    # Cert chain
    for idx, cert in enumerate(report.cert_chain):
        cert_table = Table.grid(expand=True, padding=(0, 1))
        sans_str = ', '.join(cert.san[:4])
        if len(cert.san) > 4:
            sans_str += '...'
        cert_table.add_row("[bold]Subject[/]", cert.subject)
        cert_table.add_row("Issuer", cert.issuer)
        cert_table.add_row("Valid", f"{cert.not_before[:10]} → {cert.not_after[:10]}")
        cert_table.add_row("SANs", sans_str)
        cert_table.add_row("Key", f"{cert.key_type}-{cert.key_size}")
        cert_table.add_row("Sig", cert.sig_algo)
        console.print(Panel(cert_table, title=f"Certificate {idx+1}/{len(report.cert_chain)}", box=box.MINIMAL))

    # Chain & HSTS
    console.print(f"[bold]Chain Valid:[/] {'[green]Yes[/]' if report.chain_valid else '[red]No[/]'}")
    if report.hsts:
        hsts_str = f"max-age={report.hsts.get('max_age', 0)}"
        if report.hsts.get('includesubdomains'):
            hsts_str += ", subdomains"
        if report.hsts.get('preload'):
            hsts_str += ", preload"
        console.print(f"[bold green]HSTS:[/] {hsts_str}")

    # Grade
    grade_colors = {'A': 'green', 'B': 'yellow', 'C': 'orange1', 'D': 'red', 'F': 'red'}
    color = grade_colors.get(report.security_grade, 'red')
    console.print(Panel(
        f"[bold white on {color}]{report.security_grade}[/]",
        title="[bold]Security Grade[/]",
        box=box.HEAVY
    ))