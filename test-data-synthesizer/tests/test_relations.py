from test_data_synthesizer.relations import RelationGraph

def test_topo_sort():
    g = RelationGraph()
    g.add_fk('users', 'orders')
    assert len(g.edges) == 1