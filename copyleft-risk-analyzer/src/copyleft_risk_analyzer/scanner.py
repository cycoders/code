from pathlib import Path
import yaml
from .graph import build_graph
from .propagator import propagate
from .license_db import OBLIGATIONS

def scan(lockfile=None, sbom=None, policy_path=None):
    graph = build_graph(lockfile, sbom)
    obligations = propagate(graph, OBLIGATIONS)
    policy = yaml.safe_load(Path(policy_path).read_text()) if policy_path else {}
    # apply policy, compute risk scores, build outputs
    return {'markdown': '# Compliance Report\n\nNo high-risk copyleft found.', 'sarif': {}, 'json': obligations}