from pathlib import Path
from typing import Dict, Set
import pydot

def render_graph(graph: Dict[str, Set[str]], output: Path):
    fmt = _detect_format(output)
    if fmt == 'mermaid':
        _write_mermaid(graph, output)
    else:
        _write_pydot(graph, output, fmt)

def format_mermaid(graph: Dict[str, Set[str]]) -> str:
    lines = ['```mermaid\ngraph TD']
    for caller in sorted(graph):
        for callee in sorted(graph[caller]):
            safe_c = caller.replace('.', '_').replace('<', 'L_').replace('>', 'G_')
            safe_e = callee.replace('.', '_').replace('<', 'L_').replace('>', 'G_')
            lines.append(f"  {safe_c}[\"{caller}\"] --> {safe_e}[\"{callee}\"]")
    lines.append('```')
    return '\n'.join(lines)

def _detect_format(p: Path) -> str:
    ext = p.suffix.lstrip('.')
    if ext in ('md', 'mmd'):
        return 'mermaid'
    if ext == 'dot':
        return 'dot'
    if ext in ('png', 'svg', 'pdf'):
        return ext
    raise ValueError(f'Unknown format: {ext}')

def _write_mermaid(graph: Dict[str, Set[str]], p: Path):
    p.write_text(format_mermaid(graph))

def _write_pydot(graph: Dict[str, Set[str]], p: Path, fmt: str):
    dotg = pydot.Dot(graph_type='digraph', rankdir='TB')
    for caller in graph:
        n1 = pydot.Node(caller, shape='box', style='rounded,filled', fillcolor='#e1f5fe')
        dotg.add_node(n1)
        for callee in graph[caller]:
            n2 = pydot.Node(callee, shape='box', style='rounded,filled', fillcolor='#f1f8e9')
            dotg.add_node(n2)
            e = pydot.Edge(caller, callee, color='#1976d2')
            dotg.add_edge(e)
    try:
        if fmt == 'dot':
            dotg.write_dot(str(p))
        else:
            dotg.write(str(p), format=fmt)
    except Exception:
        fallback = p.with_suffix('.dot')
        dotg.write_dot(str(fallback))
        sys.stderr.write(f'Graphviz missing. Saved DOT: {fallback}\n')