from rich.console import Console, ConsoleOptions
from rich.text import Text
from rich.table import Table
from rich.panel import Panel

from .core import RegexTester, MatchResult


def render_pattern(console: Console, tester: RegexTester) -> None:
    panel = Panel(
        f"[bold magenta]Pattern:[/] {tester.pattern}\n[bold green]Flags:[/] {tester.flags_str}",
        title="[bold cyan]Regex[/]",
        border_style="cyan",
    )
    console.print(panel)


def get_explanation(pattern: str, flags_int: int) -> str:
    flag_desc = {
        re.I: "case-insensitive (i)",
        re.M: "multiline (^/$ per line) (m)",
        re.S: "dot matches all incl. newline (s)",
        re.X: "verbose (ignore ws/comments) (x)",
    }
    active_flags = [desc for fl, desc in flag_desc.items() if flags_int & fl]
    flags_part = "; ".join(active_flags) if active_flags else "standard flags"

    constructs = [
        (r"\\d", "digit [0-9]"),
        (r"\\D", "non-digit"),
        (r"\\w", "word char [a-zA-Z0-9_]"),
        (r"\\W", "non-word"),
        (r"\\s", "whitespace"),
        (r"\\S", "non-whitespace"),
        (r"\[.*?\]", "character class [abc]"),
        (r"\\(", "capturing group (abc)"),
        (r"\\?", "zero-or-one ? or reluctant"),
        (r"\\*", "zero-or-more *"),
        (r"\\+", "one-or-more +"),
        (r"\{", "repetition {n} {n,} {n,m}"),
        (r"\^", "start-of-line ^"),
        (r"\$", "end-of-line $"),
        (r"\\b", "word boundary \\b"),
        (r"\\B", "non-word boundary \\B"),
        (r"\\A", "string start \\A"),
        (r"\\Z", "string end \\Z"),
        (r"\\.", "any char except newline (unless /s)"),
    ]
    found = []
    for pat, desc in constructs:
        if re.search(pat, pattern, re.VERBOSE):
            found.append(desc)
    constructs_part = "; ".join(found) if found else "custom/basic pattern"

    return f"{constructs_part}\nFlags: {flags_part}"


def render_test_result(console: Console, text: str, matches: list[MatchResult]) -> None:
    if not matches:
        console.print("[bold red]❌ No matches[/]")
        return

    console.print(f"[bold green]✅ {len(matches)} match(es) found[/]")

    # Highlighted text
    highlighted = Text()
    last_end = 0
    colors = ["yellow", "cyan", "magenta", "green", "blue"]
    for i, match in enumerate(matches):
        highlighted.append(text[last_end : match.start], style="white")
        style = f"bold {colors[i % len(colors)]}"
        highlighted.append(text[match.start : match.end], style=style)
        last_end = match.end
    highlighted.append(text[last_end:], style="white")
    console.print(highlighted)

    # Matches table
    table = Table(title="Matches", show_header=True, header_style="bold magenta", expand=True)
    table.add_column("#", style="cyan")
    table.add_column("Start", justify="right")
    table.add_column("End", justify="right")
    table.add_column("Len", justify="right")
    table.add_column("Main match")
    for i, match in enumerate(matches):
        main_match = text[match.start : match.end]
        table.add_row(
            str(i + 1),
            str(match.start),
            str(match.end),
            str(match.end - match.start),
            f'"{main_match[:40]}{ "..." if len(main_match) > 40 else "" }"',
        )
    console.print(table)

    # Groups for first match
    first = matches[0]
    if first.groups:
        gtable = Table(
            title="[blue]Captured Groups (first match)[/]", show_header=True, header_style="bold blue"
        )
        gtable.add_column("#", style="cyan", justify="right")
        gtable.add_column("Value")
        for j, gval in enumerate(first.groups, 1):
            display = repr(gval) if gval is not None else "None"
            gtable.add_row(str(j), display)
        console.print(gtable)


def render_explanation(console: Console, tester: RegexTester) -> None:
    explanation = get_explanation(tester.pattern, tester.flags_int)
    console.print(Panel(explanation, title="[bold blue]Explanation[/]", border_style="blue"))
