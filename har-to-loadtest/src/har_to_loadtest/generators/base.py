from abc import ABC, abstractmethod
from typing import List

from har_to_loadtest.model import HttpRequest


class Generator(ABC):
    """Base class for load test generators."""

    def __init__(
        self,
        requests: List[HttpRequest],
        vus: int = 10,
        duration: str = "30s",
        think_time: float = 1.0,
    ):
        self.requests = requests
        self.vus = vus
        self.duration = duration
        self.think_time = think_time

    @abstractmethod
    def generate(self) -> str:
        """Generate the load test script source code."""
        ...

    def _host(self) -> str:
        if not self.requests:
            return "example.com"
        from urllib.parse import urlparse
        parsed = urlparse(self.requests[0].url)
        return parsed.netloc or "example.com"
