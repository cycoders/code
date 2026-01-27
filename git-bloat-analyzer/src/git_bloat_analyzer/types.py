from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class BlobInfo:
    sha: str
    path: str
    size: int
    size_str: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class PackInfo:
    pack_file: str
    pack_size: int
    obj_count: int
    total_obj_size: int
    compression_ratio: float
    pack_size_str: str = ""
    total_obj_size_str: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class RepoStats:
    count_objects: Dict[str, str]
    disk_usage: int
    disk_usage_str: str = ""
    bloat_score: float = 0.0  # heuristic: (disk - pack)/disk

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "count_objects": self.count_objects,
        }