from typing import List, Callable, Dict, Any
from .types import Issue


Rule = Callable[[Dict[str, Any], str], List[Issue]]


def get_all_rules() -> List[Rule]:
    return [
        no_latest_image_tag,
        missing_resource_requests,
        missing_resource_limits,
        privileged_container,
        root_user_container,
        no_run_as_non_root,
        host_port_used,
        host_network_enabled,
        missing_liveness_probe,
        missing_readiness_probe,
        empty_dir_volume,
        service_load_balancer_prod,
    ]


def no_latest_image_tag(manifest: Dict[str, Any], resource_id: str) -> List[Issue]:
    issues = []
    containers = _get_containers(manifest)
    for i, cont in enumerate(containers):
        image = cont.get("image", "")
        if ":latest" in image:
            issues.append(
                Issue(
                    resource_id,
                    "MEDIUM",
                    "Avoid 'latest' image tags",
                    f"spec.template.spec.containers[{i}].image",
                    "Pin to semantic version (e.g., nginx:1.25.3)",
                )
            )
    return issues


def missing_resource_requests(manifest: Dict[str, Any], resource_id: str) -> List[Issue]:
    issues = []
    containers = _get_containers(manifest)
    for i, cont in enumerate(containers):
        resources = cont.get("resources", {})
        requests = resources.get("requests")
        if not requests or not requests.get("cpu") or not requests.get("memory"):
            issues.append(
                Issue(
                    resource_id,
                    "HIGH",
                    "Missing resource requests",
                    f"spec.template.spec.containers[{i}].resources.requests",
                    "Add cpu/memory requests based on benchmarks",
                )
            )
    return issues


def missing_resource_limits(manifest: Dict[str, Any], resource_id: str) -> List[Issue]:
    issues = []
    containers = _get_containers(manifest)
    for i, cont in enumerate(containers):
        resources = cont.get("resources", {})
        limits = resources.get("limits")
        if not limits or not limits.get("cpu") or not limits.get("memory"):
            issues.append(
                Issue(
                    resource_id,
                    "MEDIUM",
                    "Missing resource limits",
                    f"spec.template.spec.containers[{i}].resources.limits",
                    "Add cpu/memory limits to prevent OOM",
                )
            )
    return issues


def privileged_container(manifest: Dict[str, Any], resource_id: str) -> List[Issue]:
    issues = []
    containers = _get_containers(manifest)
    for i, cont in enumerate(containers):
        sec_ctx = cont.get("securityContext", {})
        if sec_ctx.get("privileged"):
            issues.append(
                Issue(
                    resource_id,
                    "HIGH",
                    "Privileged container detected",
                    f"spec.template.spec.containers[{i}].securityContext.privileged",
                    "Set privileged: false; use capabilities if needed",
                )
            )
    return issues


def root_user_container(manifest: Dict[str, Any], resource_id: str) -> List[Issue]:
    issues = []
    containers = _get_containers(manifest)
    for i, cont in enumerate(containers):
        sec_ctx = cont.get("securityContext", {})
        run_as_user = sec_ctx.get("runAsUser")
        if run_as_user == 0:
            issues.append(
                Issue(
                    resource_id,
                    "HIGH",
                    "Container runs as root (UID 0)",
                    f"spec.template.spec.containers[{i}].securityContext.runAsUser",
                    "Set runAsNonRoot: true or runAsUser: 1000+",
                )
            )
    return issues


def no_run_as_non_root(manifest: Dict[str, Any], resource_id: str) -> List[Issue]:
    issues = []
    containers = _get_containers(manifest)
    for i, cont in enumerate(containers):
        sec_ctx = cont.get("securityContext", {})
        if not sec_ctx.get("runAsNonRoot"):
            issues.append(
                Issue(
                    resource_id,
                    "MEDIUM",
                    "Missing runAsNonRoot",
                    f"spec.template.spec.containers[{i}].securityContext.runAsNonRoot",
                    "Set runAsNonRoot: true",
                )
            )
    return issues


def host_port_used(manifest: Dict[str, Any], resource_id: str) -> List[Issue]:
    issues = []
    containers = _get_containers(manifest)
    for i, cont in enumerate(containers):
        ports = cont.get("ports", [])
        for j, port in enumerate(ports):
            if port.get("hostPort"):
                issues.append(
                    Issue(
                        resource_id,
                        "HIGH",
                        "HostPort binds to node ports",
                        f"spec.template.spec.containers[{i}].ports[{j}].hostPort",
                        "Use NodePort/LoadBalancer services instead",
                    )
                )
    return issues


def host_network_enabled(manifest: Dict[str, Any], resource_id: str) -> List[Issue]:
    pod_spec = _get_pod_spec(manifest)
    if pod_spec.get("hostNetwork"):
        return [Issue(resource_id, "HIGH", "hostNetwork enabled", "spec.template.spec.hostNetwork", "Avoid; use DaemonSet or Multus CNI")]
    return []


def missing_liveness_probe(manifest: Dict[str, Any], resource_id: str) -> List[Issue]:
    issues = []
    containers = _get_containers(manifest)
    for i, cont in enumerate(containers):
        if not cont.get("livenessProbe"):
            issues.append(
                Issue(
                    resource_id,
                    "MEDIUM",
                    "Missing liveness probe",
                    f"spec.template.spec.containers[{i}].livenessProbe",
                    "Add HTTP/TCP/exec probe",
                )
            )
    return issues


def missing_readiness_probe(manifest: Dict[str, Any], resource_id: str) -> List[Issue]:
    issues = []
    containers = _get_containers(manifest)
    for i, cont in enumerate(containers):
        if not cont.get("readinessProbe"):
            issues.append(
                Issue(
                    resource_id,
                    "LOW",
                    "Missing readiness probe",
                    f"spec.template.spec.containers[{i}].readinessProbe",
                    "Add HTTP/TCP/exec probe",
                )
            )
    return issues


def empty_dir_volume(manifest: Dict[str, Any], resource_id: str) -> List[Issue]:
    issues = []
    pod_spec = _get_pod_spec(manifest)
    volumes = pod_spec.get("volumes", [])
    for i, vol in enumerate(volumes):
        if vol.get("emptyDir") and not vol["emptyDir"].get("sizeLimit"):
            issues.append(
                Issue(
                    resource_id,
                    "MEDIUM",
                    "emptyDir without sizeLimit",
                    f"spec.template.spec.volumes[{i}].emptyDir",
                    "Add sizeLimit or use PVC",
                )
            )
    return issues


def service_load_balancer_prod(manifest: Dict[str, Any], resource_id: str) -> List[Issue]:
    if manifest.get("kind") != "Service":
        return []
    metadata = manifest.get("metadata", {})
    ns = metadata.get("namespace", "default")
    if "prod" in ns.lower():
        spec = manifest.get("spec", {})
        if spec.get("type") == "LoadBalancer":
            return [Issue(resource_id, "LOW", "LoadBalancer in prod namespace", "spec.type", "Consider Ingress + controller")]
    return []


def _get_containers(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    pod_spec = _get_pod_spec(manifest)
    return pod_spec.get("containers", [])


def _get_pod_spec(manifest: Dict[str, Any]) -> Dict[str, Any]:
    spec = manifest.get("spec", {})
    return spec.get("template", {}).get("spec", {})
