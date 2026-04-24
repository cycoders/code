import typer
import rich.console
import rich.table
from pathlib import Path
from typing import List, Optional

import password_strength_simulator

from . import __version__
from .simulator import (
    estimate,
    print_table,
    print_chart,
    analyze_password,
    compute_log10_attempts,
    CrackResult,
)
from .hardware import (
    get_log10_speed,
    list_algos,
    list_hardware,
    HARDWARES,
)
from .benchmark import benchmark_algo


console = rich.console.Console()
app = typer.Typer(rich_markup_mode="rich")


@app.command(help="Estimate crack time for a password")
def estimate_cmd(
    password: str,
    algo: str = typer.Argument("bcrypt", help="Hashing algorithm"),
    cost: int = typer.Option(12, help="Cost param (bcrypt:12, PBKDF2:iters)"),
    hardware: str = typer.Option("rtx4090", help="Attacker hardware"),
    charset_size: int = typer.Option(95, help="Attacker charset size (26/62/95)"),
    local_bench: bool = typer.Option(False, "--local-bench", help="Benchmark local CPU"),
):
    if local_bench:
        log_speed = benchmark_algo(algo, cost)
        console.print(f"[yellow]Local bench: 10^{log_speed:.2f} H/s (~{10**log_speed:.0f} H/s)[/yellow]")
    else:
        log_speed = get_log10_speed(algo, cost, hardware)

    length, _ = analyze_password(password, charset_size)
    log_att = compute_log10_attempts(charset_size, length)
    res = CrackResult(log_att, log_speed)

    time_str, color = res.format_time(console)
    danger_emoji = "🔴" if "danger" in color else "🟡" if "risky" in color else "🟢"
    console.print(f"{danger_emoji} '{password}' ({length} chars, charset={charset_size}): [bold {color}]{time_str}[/{color}]")

    # Full table
    results = []
    for hw in HARDWARES:
        log_sp_hw = get_log10_speed(algo, cost, hw)
        res_hw = CrackResult(log_att, log_sp_hw)
        results.append((hw, res_hw))
    print_table(results, console)


@app.command(help="Batch estimate from file")
def batch(
    file: Path = typer.Argument(Path("passwords.txt"), help="File with pw per line"),
    algo: str = "bcrypt",
    cost: int = 12,
    hardware: str = "rtx4090",
    charset_size: int = 95,
    output: typer.FileMode = typer.Option("table", "--output", help="table/csv"),
):
    if not file.exists():
        raise typer.Abort(f"File not found: {file}")

    passwords = [line.strip() for line in file.read_text().splitlines() if line.strip()]
    log_sp = get_log10_speed(algo, cost, hardware)

    table = rich.table.Table(title="Batch Results")
    table.add_column("Password")
    table.add_column("Length")
    table.add_column("Time")

    for pw in passwords:
        length, _ = analyze_password(pw, charset_size)
        log_att = compute_log10_attempts(charset_size, length)
        res = CrackResult(log_att, log_sp)
        time_str, color = res.format_time(console)
        table.add_row(pw[:20] + "..." if len(pw)>20 else pw, str(length), f"[{color}]{time_str}[/{color}]")

    console.print(table)


@app.command(help="Generate crack time chart vs length")
def chart(
    algo: str,
    cost: int,
    hardware: str,
    charset_size: int = 95,
    min_length: int = 6,
    max_length: int = 20,
):
    print_chart(algo, cost, hardware, charset_size, min_length, max_length, console)


@app.command(help="Benchmark algo on local CPU")
def benchmark(
    algo: str,
    cost: int = 12,
    duration: float = 2.0,
    processes: Optional[int] = None,
):
    log_hps = benchmark_algo(algo, cost, duration, processes)
    hps = 10**log_hps
    console.print(f"[green]Benchmark {algo} cost={cost}: {hps:,.0f} H/s (log10={log_hps:.2f})[/green]")


@app.command()
def list(
    what: str = typer.Argument("hardware", help="hardware|algos"),
):
    if what == "hardware":
        console.print("\n".join(list_hardware()))
    elif what == "algos":
        console.print("\n".join(list_algos()))


@app.command(help="Show version")
def version():
    console.print(f"pss v{__version__}")


if __name__ == "__main__":
    app()