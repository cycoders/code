from rich.console import Console

console = Console()

def report_violations(violations: list[str]) -> None:
    if not violations:
        console.print("[green]No causality violations detected[/]")
    else:
        for v in violations:
            console.print(f"[red]✖[/] {v}")