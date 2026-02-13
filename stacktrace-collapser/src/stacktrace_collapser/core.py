from typing import List
from .models import Frame


def collapse_frames(frames: List[Frame], threshold: int = 2) -> List[Frame]:
    """
    Collapse consecutive identical frames if count >= threshold.

    Preserves order (deepest first).
    """
    if not frames:
        return []

    collapsed: List[Frame] = []
    current_group: List[Frame] = [frames[0]]

    for frame in frames[1:]:
        # Identical frame?
        prev = current_group[0]
        if (
            frame.file == prev.file
            and frame.func == prev.func
            and frame.line == prev.line
            and len(current_group) < 100  # Sanity limit
        ):
            current_group.append(frame)
        else:
            _append_group(collapsed, current_group, threshold)
            current_group = [frame]

    _append_group(collapsed, current_group, threshold)
    return collapsed


def _append_group(collapsed: List[Frame], group: List[Frame], threshold: int):
    if len(group) >= threshold:
        first = group[0].model_copy(update={"count": len(group)})
        collapsed.append(first)
    else:
        collapsed.extend(group)
