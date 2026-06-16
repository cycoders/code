import click
from rich.console import Console
from .parser import load_from_cluster, load_from_manifests
from .graph import build_graph, find_escalation_paths
from .render import render_html, render_mermaid

console = Console()

@click.command()
@click.option('--context', help='Kubeconfig context')
@click.option('--manifests', type=click.Path(exists=True), help='Directory of YAML manifests')
@click.option('--output', type=click.Choice(['html', 'mermaid', 'json']), default='html')
def main(context, manifests, output):
    """Visualize and audit RBAC policies."""
    if manifests:
        objects = load_from_manifests(manifests)
    else:
        objects = load_from_cluster(context)
    graph = build_graph(objects)
    paths = find_escalation_paths(graph)
    if output == 'html':
        render_html(graph, paths)
    elif output == 'mermaid':
        console.print(render_mermaid(graph))
    else:
        console.print_json(data={'paths': paths})