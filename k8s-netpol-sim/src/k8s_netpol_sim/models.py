from typing import Dict, List, Optional, Union

import pydantic


class LabelSelector(pydantic.BaseModel):
    """Simplified Kubernetes LabelSelector (matchLabels only)."""

    match_labels: Optional[Dict[str, str]] = None


class Peer(pydantic.BaseModel):
    """Policy peer (podSelector/namespaceSelector)."""

    pod_selector: Optional[LabelSelector] = None
    namespace_selector: Optional[LabelSelector] = None


class Rule(pydantic.BaseModel):
    """Ingress/Egress rule (peers + ports)."""

    peers: List[Peer]
    ports: Optional[List[Union[str, int]]] = None


class NetPol(pydantic.BaseModel):
    """NetworkPolicy (K8s-like, simplified)."""

    name: Optional[str] = None
    namespace: str
    pod_selector: LabelSelector
    policy_types: Optional[List[str]] = None
    ingress: Optional[List[Rule]] = None
    egress: Optional[List[Rule]] = None


class Pod(pydantic.BaseModel):
    """Pod with labels."""

    name: str
    labels: Dict[str, str]


class NamespaceTopology(pydantic.BaseModel):
    """Namespace with pods + labels."""

    labels: Dict[str, str] = {}
    pods: Dict[str, Pod]


class Topology(pydantic.BaseModel):
    """Cluster topology."""

    namespaces: Dict[str, NamespaceTopology]