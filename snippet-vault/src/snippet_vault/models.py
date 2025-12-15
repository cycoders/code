from dataclasses import dataclass, asdict, field
from typing import List, Optional, Any
from datetime import datetime


@dataclass
class Snippet:
    id: Optional[int] = None
    title: str = ""
    language: str = "text"
    tags: List[str] = field(default_factory=list)
    content: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["tags"] = ",".join(self.tags)
        if self.created_at:
            d["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            d["updated_at"] = self.updated_at.isoformat()
        return d

    @classmethod
    def from_db_row(cls, row: tuple) -> "Snippet":
        fields = ("id", "title", "language", "tags", "content", "created_at", "updated_at")
        d = dict(zip(fields, row))
        tags_str = d.pop("tags", "")
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        return cls(tags=tags, **d)
