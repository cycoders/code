from rbac_visualizer.graph import build_graph, find_escalation_paths

def test_full_flow():
    objs = [{'kind': 'RoleBinding', 'subjects': [{'name': 'svc'}], 'roleRef': {'name': 'view'}}]
    assert len(find_escalation_paths(build_graph(objs))) == 0