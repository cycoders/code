from dataclasses import dataclass
from typing import Tuple, NamedTuple


class ArgSig(NamedTuple):
    """Immutable arg signature: name and has_default."""
    name: str
    has_default: bool


@dataclass(frozen=True)
class ApiElement:
    """
    Public API element.

    Hashable for set ops.
    """
    qualname: str
    kind: str  # 'function' or 'class'
    arg_sigs: Tuple[ArgSig, ...] = tuple()

    def __post_init__(self):
        if self.kind not in ('function', 'class'):
            raise ValueError(f'Invalid kind: {self.kind}')
