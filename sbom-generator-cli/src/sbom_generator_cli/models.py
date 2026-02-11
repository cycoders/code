from pydantic import BaseModel, Field
from typing import List


class Component(BaseModel):
    """SBOM Component model."""

    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    purl: str = Field(..., pattern=r"^pkg:[^@]+@[^@]+$"))
    type: str = Field(default="library", regex=r"^(library|application|framework|operating-system|device|file)$")
    licenses: List[str] = Field(default_factory=list)


class Detector(ABC):
    """Base class for package manager detectors."""

    @abstractmethod
    def detect(self, path: Path) -> bool:
        """Detect if this manager is present."""
        ...

    @abstractmethod
    def collect(self, path: Path) -> List[Component]:
        """Collect components."""
        ...