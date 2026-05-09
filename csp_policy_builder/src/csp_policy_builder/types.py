from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, validator


@dataclass
class Resource:
    """Represented scanned web resource."""
    url: str
    scheme: str
    host: Optional[str]
    path: str
    directive: str
    is_inline: bool = False
    hash_value: Optional[str] = None  # b64 sha256


class ScanConfig(BaseModel):
    """Configuration for scanning."""
    urls: List[str]
    max_depth: int = Field(default=2, ge=0, le=5)
    max_pages: int = Field(default=50, ge=1, le=500)
    ignore_patterns: List[str] = Field(default_factory=list)
    user_agent: str = Field(default="CSPPolicyBuilder/0.1 (+https://github.com/cycoders/code)")

    @validator('urls')
    def urls_must_not_empty(cls, v):
        if not v:
            raise ValueError('At least one URL required')
        return v


CSP_DIRECTIVES = {
    'script-src': {'tags': ['script'], 'attrs': ['src']},
    'style-src': {'tags': ['style', 'link[rel="stylesheet"]', 'link[rel=stylesheet]'], 'attrs': ['href', 'src']},
    'img-src': {'tags': ['img', 'image'], 'attrs': ['src', 'srcset', 'poster']},
    'media-src': {'tags': ['audio', 'video', 'source', 'track'], 'attrs': ['src']},
    'frame-src': {'tags': ['iframe', 'frame', 'embed', 'object'], 'attrs': ['src', 'data']},
    'font-src': {'tags': ['link[rel="stylesheet"]', '@font-face'], 'attrs': ['href']},
    'connect-src': {'tags': ['script', 'img'], 'attrs': ['src']},  # heuristic
    'object-src': {'tags': ['object'], 'attrs': ['data', 'code']},
}
