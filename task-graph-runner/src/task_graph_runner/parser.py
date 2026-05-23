import yaml
from pathlib import Path
from .models import Graph, Task

def load_graph(path: Path) -> Graph:
    data = yaml.safe_load(path.read_text())
    tasks = {t['name']: Task(**t) for t in data['tasks']}
    return Graph(tasks=tasks)