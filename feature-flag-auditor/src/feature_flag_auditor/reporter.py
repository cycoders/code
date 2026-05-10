from collections import defaultdict, Counter
from pathlib import Path
from typing import Optional, Set, Dict, Any

import yaml
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

from .types import Usage


class Report:
    def __init__(self, usages: list[Usage], active_flags: Optional[Set[str]] = None):
        self.usages = usages
        self.flag_usages = defaultdict(list)
        for u in usages:
            self.flag_usages[u.flag].append(u)

        self.stats = {
            "total_usages": len(usages),
            "unique_flags": len(self.flag_usages),
            "files_touched": len({u.file for u in usages}),
        }

        self.active_flags = active_flags or set()
        self.used_flags = set(self.flag_usages)
        self.dead_flags = self.active_flags - self.used_flags
        self.unknown_flags = self.used_flags - self.active_flags

    def console_report(self, console: Console):
        table = Table(title="Flag Usage Hotspots (Top 20)", show_header=True, header_style="bold magenta")
        table.add_column("Flag", style="cyan")
        table.add_column("# Usages", justify="right")
        table.add_column("# Files", justify="right")
        table.add_column("Sample Snippet", max_width=60)

        sorted_flags = sorted(self.flag_usages.items(), key=lambda kv: len(kv[1]), reverse=True)
        for flag, usgs in sorted_flags[:20]:
            num_files = len({u.file for u in usgs})
            snippet = usgs[0].snippet
            table.add_row(flag, str(len(usgs)), str(num_files), snippet)

        console.print("\n[bold green]📊 Audit Stats[/]")
        console.print(f"Total usages: {self.stats['total_usages']:,}")
        console.print(f"Unique flags: {self.stats['unique_flags']:,}")
        console.print(f"Files with flags: {self.stats['files_touched']:,}")

        if self.dead_flags:
            console.print("\n[bold red]💀 Dead Flags[/] (defined but unused):")
            for f in sorted(self.dead_flags)[:10]:
                console.print(f"  • {f}")

        if self.unknown_flags:
            console.print("\n[bold yellow]❓ Unknown Flags[/] (used but unmanaged):")
            for f in sorted(self.unknown_flags)[:10]:
                console.print(f"  • {f}")

        console.print("\n" + table)

    def markdown_report(self) -> str:
        md = "# Feature Flag Audit Report\n\n"
        md += f"**Stats:** {self.stats}\n\n"

        if self.dead_flags:
            md += f"## 💀 Dead Flags ({len(self.dead_flags)})\n\n"
            for f in sorted(self.dead_flags):
                md += f"- `{f}`\n"
            md += "\n"

        if self.unknown_flags:
            md += f"## ❓ Unknown Flags ({len(self.unknown_flags)})\n\n"
            for f in sorted(self.unknown_flags):
                md += f"- `{f}`\n"
            md += "\n"

        md += "## 📊 Top Flags\n\n| Flag | Usages | Files | Snippet |\n|------|---------|-------|---------|\n"
        sorted_flags = sorted(self.flag_usages.items(), key=lambda kv: len(kv[1]), reverse=True)[:20]
        for flag, usgs in sorted_flags:
            num_files = len({u.file for u in usgs})
            snippet = usgs[0].snippet[:50] + "..." if len(usgs[0].snippet) > 50 else usgs[0].snippet
            md += f"| `{flag}` | {len(usgs)} | {num_files} | `{snippet}` |\n"

        return md

    def json_report(self) -> Dict[str, Any]:
        return {
            "stats": self.stats,
            "dead_flags": sorted(self.dead_flags),
            "unknown_flags": sorted(self.unknown_flags),
            "flag_usages": {
                flag: {
                    "count": len(usgs),
                    "files": sorted({u.file.as_posix() for u in usgs}),
                    "samples": [u._asdict() for u in usgs[:3]],
                }
                for flag, usgs in self.flag_usages.items()
            },
        }
