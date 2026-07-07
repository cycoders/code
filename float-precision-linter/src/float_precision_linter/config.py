import os
from dataclasses import dataclass

@dataclass
class Config:
    tolerance: float = 1e-9

    @classmethod
    def from_env(cls):
        return cls(float(os.getenv("FPL_TOLERANCE", "1e-9")))