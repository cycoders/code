from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional


@dataclass
class LayerDelta:
    sha: str
    status: str  # 'same', 'added', 'removed', 'changed'
    size1: Optional[int] = None
    size2: Optional[int] = None
    size_delta: Optional[int] = None


@dataclass
class ConfigDelta:
    changed_keys: Dict[str, tuple[Optional[str], Optional[str]]] = field(default_factory=dict)
    added_keys: List[str] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)


@dataclass
class ImageDiff:
    image1_name: str
    image2_name: str
    size1: int
    size2: int
    size_delta: int
    num_layers1: int
    num_layers2: int
    layer_deltas: List[LayerDelta]
    config_delta: ConfigDelta
    os1: str
    os2: str
    arch1: str
    arch2: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
