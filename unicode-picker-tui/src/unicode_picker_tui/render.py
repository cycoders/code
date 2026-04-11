"""Render Unicode char views."""

from .models import UnicodeChar


def render_list_item(c: UnicodeChar, is_fav: bool = False) -> str:
    """Rich markup for ListItem."""
    fav = " 💖 " if is_fav else "    "
    return (
        f"[bold ansi_yellow]{c.char}[/bold]{fav} "
        f"[dim italic]{c.name}[/]\n"
        f"[bright_black dim]{c.codepoint} | {c.category} | {c.block.split()[-1]}[/]"
    )


def render_detail(c: UnicodeChar, is_fav: bool) -> str:
    """Rich markup for details."""
    fav_status = "(💖 Fav)" if is_fav else ""
    props = [
        f"[bold]Name[/]: {c.name} {fav_status}",
        f"[bold]Codepoint[/]: [ansi_cyan]{c.char}[/] {c.codepoint}",
        f"[bold]Category[/]: {c.category}",
        f"[bold]Block[/]: {c.block.strip('"')}",
        f"[bold]Bidi[/]: {c.bidirectional}",
        f"[bold]Mirrored[/]: {c.mirrored}",
        f"[bold]Decomp[/]: {c.decomposition or '—'}",
        f"[bold]EAW[/]: {c.east_asian_width}",
    ]
    return "\n".join(props)
