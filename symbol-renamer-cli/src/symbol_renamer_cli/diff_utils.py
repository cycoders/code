from difflib import unified_diff

from pathlib import Path
from rich.console import Console
from rich.panel import Panel


def show_preview(
    old_code: str, new_code: str, file_path: Path, console: Console
) -> None:
    """Display colorized unified diff in a Rich panel."""
    diff_lines = list(
        unified_diff(
            old_code.splitlines(keepends=True),
            new_code.splitlines(keepends=True),
            str(file_path),
            f"{file_path} (renamed)",
            n=3,
        )
    )

    if not diff_lines:
        return

    colored_lines = []
    for line in diff_lines:
        stripped = line.rstrip("\r\n")
        if line.startswith("--- ") or line.startswith("+++ "):
            colored_lines.append(f"[dim]{stripped}[/]")
        elif line.startswith("@@ "):
            colored_lines.append(f"[blue]{stripped}[/]")
        elif line.startswith("+"):
            colored_lines.append(f"[green]{stripped}[/]")
        elif line.startswith("-"):
            colored_lines.append(f"[red]{stripped}[/]")
        else:
            colored_lines.append(f"{stripped}")

    diff_text = "\n".join(colored_lines) + "\n"
    console.print(
        Panel(
            diff_text,
            title=f"Preview: {file_path.name}",
            border_style="yellow",
            expand=False,
        )
    )