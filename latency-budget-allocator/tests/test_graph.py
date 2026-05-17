import tempfile
from latency_budget_allocator.graph import load_graph

def test_load_graph():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write('api: {}\n')
        f.flush()
        graph = load_graph(f.name)
        assert 'api' in graph