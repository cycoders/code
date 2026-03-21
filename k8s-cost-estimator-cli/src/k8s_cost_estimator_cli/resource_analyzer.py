from typing import Dict, Any, Tuple
from .types import Resources


def extract_resources(obj: Dict[str, Any], nodes: int = 1) -> Resources:
    """Extract aggregated CPU/memory requests from K8s object."""
    resources = Resources(cpu_cores=0.0, mem_gib=0.0)

    kind = obj["kind"]
    spec = obj.get("spec", {})

    # Replicas
    replicas = spec.get("replicas", 1)
    if kind == "DaemonSet":
        replicas = nodes

    # HPA scaling (average)
    hpa_target = _extract_hpa_target(obj)
    if hpa_target:
        replicas = (replicas + hpa_target) / 2  # Simple avg

    # Template
    template = spec.get("template", {}).get("spec", {})
    containers = template.get("containers", [])

    pod_resources = _pod_resources(containers)
    resources.cpu_cores = pod_resources.cpu_cores * replicas
    resources.mem_gib = pod_resources.mem_gib * replicas

    return resources


def _extract_hpa_target(obj: Dict[str, Any]) -> int | None:
    autos = obj.get("spec", {}).get("autoscaling", {})
    return autos.get("targetCPUUtilizationPercentage")


def _pod_resources(containers: list[Dict[str, Any]]) -> Resources:
    cpu = mem_mi = 0.0
    for cont in containers:
        reqs = cont.get("resources", {}).get("requests", {})
        cpu += _cpu_to_cores(reqs.get("cpu", "0"))
        mem_mi += _mem_to_mib(reqs.get("memory", "0Mi"))
    return Resources(cpu_cores=cpu, mem_gib=mem_mi / 1024)


def _cpu_to_cores(cpu: str) -> float:
    if "m" in cpu:
        return int(cpu[:-1]) / 1000
    return float(cpu or 0)


def _mem_to_mib(mem: str) -> float:
    if mem.endswith("Gi"):
        return float(mem[:-2]) * 1024
    elif mem.endswith("Mi"):
        return float(mem[:-2])
    elif mem.endswith("GiB"):
        return float(mem[:-3]) * 1024
    return float(mem or 0)
