from pathlib import Path
import yaml
from kubernetes import client, config

def load_from_cluster(context=None):
    config.load_kube_config(context=context)
    v1 = client.RbacAuthorizationV1Api()
    return (list(v1.list_cluster_role_binding().items) +
            list(v1.list_role_binding_for_all_namespaces().items))

def load_from_manifests(path):
    objects = []
    for f in Path(path).rglob('*.yaml'):
        for doc in yaml.safe_load_all(f.read_text()):
            if doc and doc.get('kind') in ('Role', 'ClusterRole', 'RoleBinding', 'ClusterRoleBinding'):
                objects.append(doc)
    return objects