"""Cycle classification logic."""
from enum import Enum

class CycleType(Enum):
    CONTAINER = "container"
    CALLBACK = "callback"
    DATACLASS = "dataclass"