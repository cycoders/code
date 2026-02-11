import docker
import tempfile
import os
import shutil
from typing import Dict, Any, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn

client = docker.from_env(version="auto", version_prefix="auto")


def ensure_image_loaded(image_name: str) -> docker.models.images.Image:
    """Load or pull image with progress."""
    try:
        return client.images.get(image_name)
    except docker.errors.NotFound:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task(f"Pulling {image_name}", total=None)
            for _ in client.images.pull(image_name, stream=True, decode=True):
                pass  # Progress via docker
            progress.remove_task(task)
        return client.images.get(image_name)


def get_image_info(img: docker.models.images.Image) -> Dict[str, Any]:
    """Extract structured info from image."""
    attrs = img.attrs
    history = img.history()
    layer_sizes = {h["Id"]: h.get("Size", 0) for h in history}
    rootfs_layers = attrs["RootFS"].get("Layers", [])

    return {
        "attrs": attrs,
        "history": history,
        "layer_sizes": layer_sizes,
        "rootfs_layers": rootfs_layers,
    }