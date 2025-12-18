from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class Job:
    name: str
    cron: str
    duration: int = 60  # seconds


@dataclass
class Execution:
    job_name: str
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError("end must be after start")
