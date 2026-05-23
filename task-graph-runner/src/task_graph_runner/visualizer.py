import networkx as nx

def to_mermaid(graph) -> str:
    lines = ["graph TD"]
    for name, task in graph.tasks.items():
        for dep in task.deps:
            lines.append(f"    {dep} --> {name}")
    return "\n".join(lines)