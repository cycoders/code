import graphviz
from typing import List, Union
from rich.console import Console, ConsoleRenderable
from rich.tree import Tree
from rich.text import Text

from .tree_builder import DepNode

RenderResult = Union[str, bytes]
RenderError = ValueError

ICONS = {
    "poetry": "🐍",
    "npm": "🔗",
    "cargo": "🦀",
}

def render(forest: List[DepNode], fmt: str) -> RenderResult:
    fmt = fmt.lower()
    if fmt == "ascii":
        return _render_ascii(forest)
    if fmt in ("mermaid", "mmd"):
        return _render_mermaid(forest)
    if fmt == "png":
        return _render_graphviz(forest, "png")
    if fmt == "svg":
        return _render_graphviz(forest, "svg")
    raise RenderError(f"Unsupported format '{fmt}'. Use ascii, mermaid, png, svg.")

def _render_ascii(forest: List[DepNode]) -> str:
    console = Console(width=120)
    with console.capture() as capture:
        if not forest:
            console.print("[yellow]No dependencies[/yellow]")
            return capture.get()

        if len(forest) == 1:
            tree = Tree(_format_label(forest[0].namever), guide_style="dim", expand=True)
            _populate_tree(tree, forest[0])
        else:
            tree = Tree("📦 Dependencies", guide_style="cyan", expand=True)
            for node in forest:
                sub_tree = Tree(_format_label(node.namever), style="bold green", guide_style="dim")
                _populate_tree(sub_tree, node)
                tree.add(sub_tree)
            console.print(tree)
    return capture.text

def _format_label(namever: str) -> str:
    if "@" in namever:
        name, ver = namever.split("@", 1)
        return f"[bold cyan]{name}[/bold cyan]@[italic dim]{ver}[/]"
    return f"[bold cyan]{namever}[/bold cyan]"

def _populate_tree(rtree: Tree, node: DepNode) -> None:
    for child in node.children:
        child_tree = Tree(_format_label(child.namever), guide_style="dim", expand=True)
        rtree.add(child_tree)
        _populate_tree(child_tree, child)

def _render_mermaid(forest: List[DepNode]) -> str:
    lines = ["flowchart TD", "classDef dep fill:#e1f5fe,stroke:#01579b,stroke-width:2px"]
    id_map: Dict[str, str] = {}
    next_id = 0

    def get_id(nv: str) -> str:
        nonlocal next_id
        if nv not in id_map:
            id_map[nv] = f"N{next_id}"
            next_id += 1
        return id_map[nv]

    for root_node in forest:
        _traverse_mermaid(root_node, lines, get_id)
    lines.append("class " + " ".join(id_map.values()) + " dep")
    return "\n".join(lines)

def _traverse_mermaid(node: DepNode, lines: List[str], get_id) -> None:
    nid = get_id(node.namever)
    name, ver = node.namever.split("@", 1)
    label = f"{name}\\n{ver[:20]}"
    lines.append(f'{nid}["{label}"]')
    for child in node.children:
        cid = get_id(child.namever)
        lines.append(f"{nid} --> {cid}")
        _traverse_mermaid(child, lines, get_id)

def _render_graphviz(forest: List[DepNode], outfmt: str) -> bytes:
    dot = graphviz.Digraph(comment="Dependency Graph", format=outfmt)
    dot.attr("graph", rankdir="TB", splines="ortho", bgcolor="#f8f9fa")
    dot.attr("node", shape="box", style="rounded,filled", fillcolor="#e3f2fd", fontsize="10")
    dot.attr("edge", color="#1976d2")

    id_map: Dict[str, str] = {}
    next_id = 0

    def get_id(nv: str) -> str:
        nonlocal next_id
        if nv not in id_map:
            id_map[nv] = str(next_id)
            next_id += 1
        return id_map[nv]

    for root_node in forest:
        _traverse_gv(root_node, dot, get_id)

    return dot.pipe()

def _traverse_gv(node: DepNode, dot: graphviz.Digraph, get_id) -> None:
    nid = get_id(node.namever)
    name, ver = node.namever.split("@", 1)
    label = f"{name}\n{ver}"
    dot.node(nid, label=label)
    for child in node.children:
        cid = get_id(child.namever)
        dot.edge(nid, cid)
        _traverse_gv(child, dot, get_id)