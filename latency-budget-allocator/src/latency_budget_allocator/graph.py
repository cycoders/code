import yaml

def load_graph(path: str) -> dict:
    """Load service dependency graph from YAML."""
    with open(path) as f:
        return yaml.safe_load(f)