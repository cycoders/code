from copyleft_risk_analyzer.graph import build_graph

def test_empty_graph():
    assert build_graph(None, None) == {'nodes': [], 'edges': []}