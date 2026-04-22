import yaml
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field, validator


from .types import LayerConfig  # wait no, define here


class Layer(BaseModel):
    name: str
    package_prefixes: List[str]
    allowed_layers: List[str] = Field(default_factory=list)
    forbidden_layers: List[str] = Field(default_factory=list)


class Config(BaseModel):
    layers: List[Layer]
    src_dir: str = "src"
    ignore_globs: List[str] = Field(default_factory=list)
    allow_third_party: bool = True

    @classmethod
    def load(cls, file_path: Path) -> "Config":
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)

    def to_yaml(self, file_path: Path):
        with open(file_path, "w") as f:
            yaml.safe_dump(self.model_dump(), f, default_flow_style=False, sort_keys=False)