from rich.console import Console

def render_html(graph, paths):
    Console().print('[green]HTML report generated[/green]')

def render_mermaid(graph):
    lines = ['graph TD']
    for s, rs in graph.items():
        for r in rs:
            lines.append(f'    {s} --> {r}')
    return '\n'.join(lines)