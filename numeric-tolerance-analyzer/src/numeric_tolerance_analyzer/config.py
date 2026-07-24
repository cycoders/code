from dataclasses import dataclass

@dataclass
class Config:
    min_tol: float = 1e-12
    max_tol: float = 1e-3
    format: str = "text"