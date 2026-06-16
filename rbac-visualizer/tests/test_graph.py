from rbac_visualizer.graph import build_graph, find_escalation_paths

def test_basic_graph():
    objs = [{'kind': 'ClusterRoleBinding', 'subjects': [{'name': 'dev'}], 'roleRef': {'name': 'edit'}}]
    g = build_graph(objs)
    assert 'subject:dev' in g

def test_escalation():
    objs = [{'kind': 'ClusterRoleBinding', 'subjects': [{'name': 'bad'}], 'roleRef': {'name': 'cluster-admin'}}]
    g = build_graph(objs)
    assert find_escalation_paths(g)[0]['risk'] == 'cluster-admin'