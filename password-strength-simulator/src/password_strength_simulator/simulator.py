import math

from typing import Tuple

import rich

from .hardware import get_log10_speed, list_algos, list_hardware


CHARSET_SIZES = {
    "lower": 26,
    "alphanumeric": 62,
    "printable": 95,
}


COLOR_MAP = {
    "safe": "green",
    "risky": "yellow",
    "danger": "red",
}


class CrackResult:
    def __init__(self, log10_attempts: float, log10_speed: float):
        self.log10_time_secs = log10_attempts - log10_speed

    def format_time(self, console: rich.console.Console) -> Tuple[str, str]:
        if self.log10_time_secs > 20:
            years_log10 = self.log10_time_secs - math.log10(3.15576e7)
            time_str = f"~10^{years_log10:.1f} years"
            color = "safe"
        elif self.log10_time_secs > 12:
            secs = 10 ** self.log10_time_secs
            days = secs / 86400
            time_str = f"{days:.1f} days"
            color = "risky"
        else:
            secs = 10 ** self.log10_time_secs
            if secs < 1:
                time_str = f"{secs:.3f}s"
            else:
                time_str = f"{secs:.1f}s"
            color = "danger"
        return time_str, COLOR_MAP[color]


def compute_log10_attempts(charset_size: int, length: int) -> float:
    """log10(charset_size ** length)"""
    if length == 0:
        return float("-inf")
    return length * math.log10(charset_size)


def analyze_password(pw: str, charset_size: int = 95) -> Tuple[int, int]:
    """Length and charset_size (default printable)."""
    length = len(pw)
    # Could detect min charset, but default to user/full printable
    return length, charset_size


def estimate(
    pw: str,
    algo: str,
    cost: int,
    hardware: str,
    charset_size: int = 95,
) -> CrackResult:
    length, _ = analyze_password(pw, charset_size)
    log_att = compute_log10_attempts(charset_size, length)
    log_sp = get_log10_speed(algo, cost, hardware)
    return CrackResult(log_att, log_sp)


def print_table(results: list[tuple[str, CrackResult]], console: rich.console.Console):
    table = rich.table.Table(title="Crack Times")
    table.add_column("Hardware")
    table.add_column("Attempts")
    table.add_column("Time")

    for hw, res in results:
        att_str = f"{10**res.log10_time_secs + res.log10_speed:.1e}"
        time_str, color = res.format_time(console)
        table.add_row(hw, att_str, f"[{color}]{time_str}[/{color}]")

    console.print(table)


def print_chart(
    algo: str,
    cost: int,
    hardware: str,
    charset_size: int,
    min_length: int,
    max_length: int,
    console: rich.console.Console,
):
    console.print(f"Crack time vs Length ({algo} c={cost} on {hardware}, charset={charset_size})")

    table = rich.table.Table(expand=True)
    table.add_column("Length", justify="right")
    table.add_column("Crack Time")

    log_sp = get_log10_speed(algo, cost, hardware)
    for l in range(min_length, max_length + 1):
        log_att = compute_log10_attempts(charset_size, l)
        res = CrackResult(log_att, log_sp)
        time_str, color = res.format_time(console)
        table.add_row(str(l), f"[{color}]{time_str}[/{color}]")

    console.print(table)