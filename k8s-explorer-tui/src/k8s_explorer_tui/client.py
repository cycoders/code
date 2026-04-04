'''Kubernetes API client wrapper for Explorer TUI.'''

from typing import Any, Dict, List
import logging

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

logger = logging.getLogger(__name__)


class K8sExplorerClient:
    """Lightweight client for cluster resources. Handles errors gracefully."""

    def __init__(self, context: str | None = None, default_namespace: str | None = None) -> None:
        """Initialize client, load kubeconfig."""
        try:
            config.load_kube_config(context=context)
        except Exception as e:
            msg = f"Failed to load kubeconfig (context='{context}'):\n{e}"
            logger.error(msg)
            raise RuntimeError(msg) from e

        self.default_namespace = default_namespace or "default"
        self._core_v1 = client.CoreV1Api()
        self._apps_v1 = client.AppsV1Api()

    def get_namespaces(self) -> List[str]:
        """List accessible namespaces."""
        try:
            return [item.metadata.name for item in self._core_v1.list_namespace().items]
        except ApiException as e:
            logger.error(f"API error listing namespaces: {e}")
            raise RuntimeError(f"Cannot list namespaces: {e}") from e

    def get_deployments_info(self, namespace: str) -> List[Dict[str, Any]]:
        """List deployments with ready/desired replica counts."""
        try:
            deps = self._apps_v1.list_namespaced_deployment(namespace)
            return [
                {
                    "name": d.metadata.name,
                    "ready": d.status.ready_replicas or 0 if d.status else 0,
                    "desired": d.spec.replicas or 0,
                }
                for d in deps.items
            ]
        except ApiException as e:
            logger.warning(f"Failed deployments {namespace}: {e}")
            return []

    def get_pods_info(self, namespace: str) -> List[Dict[str, Any]]:
        """List pods with status and restart count."""
        try:
            pod_list = self._core_v1.list_namespaced_pod(namespace)
            return [
                {
                    "name": p.metadata.name,
                    "status": p.status.phase if p.status else "Unknown",
                    "restarts": (
                        p.status.container_statuses[0].restart_count
                        if p.status and p.status.container_statuses
                        else 0
                    ),
                }
                for p in pod_list.items
            ]
        except ApiException as e:
            logger.warning(f"Failed pods {namespace}: {e}")
            return []

    def get_pod_logs(self, namespace: str, pod_name: str, tail_lines: int = 200) -> str:
        """Fetch recent pod logs."""
        try:
            logs = self._core_v1.read_namespaced_pod_log(
                name=pod_name, namespace=namespace, tail_lines=tail_lines
            )
            return logs
        except ApiException as e:
            msg = f"Logs {pod_name}/{namespace}: {e}"
            logger.error(msg)
            raise RuntimeError(msg) from e