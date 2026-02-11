from pathlib import Path
from typing import List

from rich.console import Console

from .detector import DetectorRegistry

from .models import Component


console = Console()


def dedupe_components(comps: List[Component]) -> List[Component]:
    """Deduplicate components by name/version."""
    seen = {(c.name.lower(), c.version): c for c in comps}
    return sorted(seen.values(), key=lambda c: c.name)


def collect_components(path: Path) -> List[Component]:
    """Collect all components from active detectors."""
    reg = DetectorRegistry(path)
    all_comps: List[Component] = []

    for detector in reg.get_active():
        try:
            comps = detector.collect(path)
            all_comps.extend(comps)
            console.print(f"[green]✓[/green] [blue]{detector.__class__.__name__}[/blue]: [cyan]{len(comps)}[/cyan] components")
        except Exception as e:
            console.print(f"[red]✗[/red] [blue]{detector.__class__.__name__}[/blue]: {e}")

    unique = dedupe_components(all_comps)
    console.print(f"[bold green]Total unique: {len(unique)}[/bold green]")
    return unique
