from typing import Type

from .base import Generator
from .k6 import K6Generator
from .locust import LocustGenerator
from .artillery import ArtilleryGenerator


_generator_map: Dict[str, Type[Generator]] = {
    "k6": K6Generator,
    "locust": LocustGenerator,
    "artillery": ArtilleryGenerator,
}


def get_generator_class(fmt: str) -> Type[Generator]:
    """Get generator class by name."""
    fmt_lower = fmt.lower()
    if fmt_lower not in _generator_map:
        raise ValueError(f"Unsupported format: {fmt}. Choose: k6, locust, artillery")
    return _generator_map[fmt_lower]
