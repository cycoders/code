import psutil
from typing import Optional

def format_node(p: "psutil.Process") -> str:
    """Format process info as rich label. Handles errors gracefully."""
    try:
        cpu = p.cpu_percent(interval=None)
        mem_info = p.memory_info()
        mem_mb = mem_info.rss / (1024 * 1024)
        name = p.name()
        cmdline = p.cmdline()
        cmd_short = " ".join(cmdline[:4]).replace("\\", "/")[:60]
        if not cmd_short:
            cmd_short = "[? unknown]"
        return (
            f"[dim cyan]{p.pid}[/] "
            f"[bold magenta]{name}[/] "
            f"[red]{cpu:.1f}%[/] "
            f"[green]{mem_mb:.0f}M[/] "
            f"[dim white]{cmd_short}[/]"
        )
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError):
        return f"[dim red]✗ {p.pid} [GONE/ZOMBIE][/bold]"
    except Exception:
        return f"[dim red]? {p.pid} [ERROR][/]"