from typing import Dict, List, Any
from .types import ImageDiff, LayerDelta, ConfigDelta
from .image import get_image_info


def compute_config_delta(config1: Dict[str, Any], config2: Dict[str, Any]) -> ConfigDelta:
    delta = ConfigDelta()
    env1 = dict(e.split("=", 1) for e in config1.get("Env", []))
    env2 = dict(e.split("=", 1) for e in config2.get("Env", []))
    labels1 = config1.get("Labels", {})
    labels2 = config2.get("Labels", {})

    # Env
    for k in set(env1) | set(env2):
        v1 = env1.get(k)
        v2 = env2.get(k)
        if v1 != v2:
            delta.changed_keys[k] = (v1, v2)
        elif k not in env1:
            delta.added_keys.append(k)
        elif k not in env2:
            delta.removed_keys.append(k)

    # Labels similar...
    for k in set(labels1) | set(labels2):
        if labels1.get(k) != labels2.get(k):
            delta.changed_keys[f"label:{k}"] = (labels1.get(k), labels2.get(k))

    return delta


def compute_diff(image1_name: str, image2_name: str) -> ImageDiff:
    img1 = ensure_image_loaded(image1_name)
    img2 = ensure_image_loaded(image2_name)
    info1 = get_image_info(img1)
    info2 = get_image_info(img2)

    attrs1 = info1["attrs"]
    attrs2 = info2["attrs"]

    # Basic
    size1 = attrs1["Size"]
    size2 = attrs2["Size"]
    size_delta = size2 - size1
    num_layers1 = len(info1["rootfs_layers"])
    num_layers2 = len(info2["rootfs_layers"])

    # Layers
    all_shas = set(info1["rootfs_layers"] + info2["rootfs_layers"])
    layer_deltas: List[LayerDelta] = []
    for sha in sorted(all_shas, reverse=True):  # Bottom-up-ish
        s1 = info1["layer_sizes"].get(sha)
        s2 = info2["layer_sizes"].get(sha)
        if sha in info1["rootfs_layers"] and sha in info2["rootfs_layers"]:
            status = "same" if s1 == s2 else "changed"
            layer_deltas.append(LayerDelta(sha[:12], status, s1, s2, s2 - s1 if s1 is not None and s2 is not None else None))
        elif sha in info1["rootfs_layers"]:
            layer_deltas.append(LayerDelta(sha[:12], "removed", s1))
        else:
            layer_deltas.append(LayerDelta(sha[:12], "added", None, s2))

    config_delta = compute_config_delta(attrs1["Config"], attrs2["Config"])

    return ImageDiff(
        image1_name=image1_name,
        image2_name=image2_name,
        size1=size1,
        size2=size2,
        size_delta=size_delta,
        num_layers1=num_layers1,
        num_layers2=num_layers2,
        layer_deltas=layer_deltas,
        config_delta=config_delta,
        os1=attrs1["Os"],
        os2=attrs2["Os"],
        arch1=attrs1["Architecture"],
        arch2=attrs2["Architecture"],
    )
