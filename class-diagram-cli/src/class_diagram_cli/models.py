from dataclasses import dataclass, field
from typing import List


@dataclass
class Method:
    """Represents a method in a class."""
    name: str
    is_static: bool = False
    is_classmethod: bool = False


@dataclass
class ClassInfo:
    """Parsed class information from AST."""
    name: str
    module: str
    bases: List[str] = field(default_factory=list)
    methods: List[Method] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)