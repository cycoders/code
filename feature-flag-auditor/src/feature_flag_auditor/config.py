from typing import List, Dict, Optional

from pydantic import BaseModel, Field, validator


class Pattern(BaseModel):
    name: str
    regex: str
    langs: List[str] = Field(default_factory=list)
    capture_group: int = 1


class Config(BaseModel):
    """Configuration for the auditor."""

    patterns: List[Pattern] = Field(default_factory=list)
    exts: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "python": ["py"],
            "js": ["js", "ts", "jsx", "tsx"],
        }
    )
    ignore_paths: List[str] = Field(
        default_factory=lambda: ".git,node_modules,dist,build,.next,out,venv,__pycache__".split(",")
    )

    @validator("exts")
    def exts_list(cls, v):
        result = {}
        for lang, lst in v.items():
            result[lang] = [f".{e}" if not e.startswith(".") else e for e in lst]
        return result

    class Config:
        extra = "forbid"
