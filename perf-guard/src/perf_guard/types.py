from typing import TypedDict, List


Times = List[float]


class Stats(TypedDict, total=True):
    mean: float
    stdev: float
    min: float
    max: float
    iterations: int
    unit: str