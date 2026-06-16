from collections import defaultdict

def build_graph(objects):
    g = defaultdict(list)
    for o in objects:
        kind = o['kind']
        if 'Binding' in kind:
            subj = o['subjects'][0]['name'] if o.get('subjects') else 'unknown'
            role = o['roleRef']['name']
            g[f'subject:{subj}'].append(f'role:{role}')
    return dict(g)

def find_escalation_paths(graph):
    risky = []
    for subj, roles in graph.items():
        if any('cluster-admin' in r or '*' in r for r in roles):
            risky.append({'subject': subj, 'risk': 'cluster-admin'})
    return risky