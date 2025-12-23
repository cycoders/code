import json
from typing import Dict, Any
from rich.console import Console, RenderableType
from rich.table import Table
from rich.tree import Tree

console = Console()


def report_console(
    data: Dict[str, Any],
    threshold: float,
    show_tree: bool = True,
    show_table: bool = True,
    show_suggestions: bool = True,
) -> None:
    total_ms = data["total_startup_time"] * 1000
    console.rule(f"[bold]Startup Profile: {total_ms:.1f}ms total[/bold]")

    modules = data["modules"]

    if show_tree:
        tree = _build_tree(modules, "__main__", threshold)
        console.print(tree)

    if show_table:
        table = _build_table(data, threshold)
        console.print(table)

    if show_suggestions:
        _print_suggestions(data, threshold)


def _build_tree(modules: Dict[str, Dict], node: str, threshold: float) -> Tree:
    if node not in modules:
        return Tree("[dim]__main__[/dim]")

    mod_data = modules[node]
    incl_ms = mod_data["inclusive"] * 1000
    excl_ms = mod_data["exclusive"] * 1000
    if incl_ms < threshold:
        return Tree(f"[dim]{node}[/dim]")

    label = f"[bold cyan]{node}[/bold cyan] [dim]({incl_ms:.0f}i/{excl_ms:.0f}e ms)[/dim]"
    tree = Tree(label)

    # Sort children by inclusive desc
    children = sorted(
        mod_data["deps"].keys(),
        key=lambda c: modules[c]["inclusive"],
        reverse=True,
    )
    for child in children:
        if modules[child]["inclusive"] * 1000 >= threshold:
            tree.add(_build_tree(modules, child, threshold))
    return tree


def _build_table(data: Dict[str, Any], threshold: float) -> Table:
    total = data["total_startup_time"]
    modules = data["modules"]

    table = Table("Module", "Incl (ms)", "Excl (ms)", "% Total", title="Top Modules")
    table.add_column("Module", style="cyan")
    table.add_column("Incl", justify="right")
    table.add_column("Excl", justify="right")
    table.add_column("%", justify="right")

    for mod, d in sorted(modules.items(), key=lambda x: x[1]["inclusive"], reverse=True):
        incl_ms = d["inclusive"] * 1000
        if incl_ms < threshold:
            continue
        excl_ms = d["exclusive"] * 1000
        pct = (d["inclusive"] / total * 100) if total > 0 else 0
        table.add_row(mod, f"{incl_ms:.1f}", f"{excl_ms:.1f}", f"{pct:.1f}%")
    return table


def _print_suggestions(data: Dict[str, Any], threshold: float) -> None:
    modules = data["modules"]
    total_ms = data["total_startup_time"] * 1000

    slow_init = [
        (m, d["exclusive"] * 1000)
        for m, d in modules.items()
        if d["exclusive"] * 1000 > 50
    ]
    deep_deps = [m for m, d in modules.items() if len(d["deps"]) > 10]

    console.print("\n[bold yellow]Suggestions[/bold yellow]")
    if total_ms > 200:
        console.print("  🚀 Total >200ms: profile deps & lazy load heavy ones")
    if slow_init:
        console.print("  🐌 Heavy module init (>50ms excl):")
        for mod, ms in sorted(slow_init, key=lambda x: x[1], reverse=True)[:3]:
            console.print(f"    [red]{mod}[/red]: {ms:.0f}ms – move to func or stub")
    if deep_deps:
        console.print(f"  🌳 Deep deps: {', '.join(deep_deps[:3])}")
    else:
        console.print("  ✅ Lean imports!")


def report_json(data: Dict[str, Any], filepath: str) -> None:
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    console.print(f"[green]JSON saved: {filepath}")


def report_html(data: Dict[str, Any], threshold_ms: float, filepath: str) -> None:
    threshold = threshold_ms / 1000
    total_ms = data["total_startup_time"] * 1000

    # Table rows
    table_rows = []
    modules = data["modules"]
    for mod, d in sorted(modules.items(), key=lambda x: x[1]["inclusive"], reverse=True):
        incl_ms = d["inclusive"] * 1000
        if incl_ms < threshold_ms:
            continue
        excl_ms = d["exclusive"] * 1000
        pct = (d["inclusive"] / data["total_startup_time"] * 100) if data["total_startup_time"] > 0 else 0
        table_rows.append(f"<tr><td>{mod}</td><td>{incl_ms:.1f}</td><td>{excl_ms:.1f}</td><td>{pct:.1f}%</td></tr>")

    # Tree HTML
    def tree_html(node: str, modules: Dict[str, Dict], depth: int = 0) -> str:
        if node not in modules:
            return ""
        d = modules[node]
        incl_ms = d["inclusive"] * 1000
        if incl_ms < threshold_ms:
            return ""
        excl_ms = d["exclusive"] * 1000
        label = f"{node} ({incl_ms:.0f}i/{excl_ms:.0f}e ms)"
        html = "  " * depth + f"<li>{label}"
        children = sorted(d["deps"], key=lambda c: modules[c]["inclusive"], reverse=True)
        if children:
            html += "<ul>" + "".join(tree_html(c, modules, depth + 1) for c in children) + "</ul>"
        html += "</li>"
        return html

    tree_str = tree_html("__main__", modules)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Import Profiler - {total_ms:.0f}ms</title>
    <style>
        body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1200px; margin:0 auto; padding:20px; }}
        h1 {{ color:#2563eb; }}
        table {{ border-collapse:collapse; width:100%; margin:20px 0; }}
        th,td {{ border:1px solid #ddd; padding:8px; text-align:left; }}
        th {{ background:#f3f4f6; }}
        ul {{ list-style:none; padding-left:20px; }}
        li {{ margin:4px 0; }}
        .slow {{ color:#ef4444; font-weight:bold; }}
    </style>
</head>
<body>
    <h1>🚀 Import Profile: {total_ms:.0f}ms total</h1>
    <h2>Top Modules</h2>
    <table>
        <tr><th>Module</th><th>Incl (ms)</th><th>Excl (ms)</th><th>% Total</th></tr>
        {''.join(table_rows)}
    </table>
    <h2>Dep Tree</h2>
    <ul>{tree_str}</ul>
</body>
</html>
"""

    with open(filepath, "w") as f:
        f.write(html)
    console.print(f"[green]HTML saved: {filepath}")
