from textual.message import Message
from typing import Dict, Any


class TaskDataUpdated(Message):
    """Posted when new task data is available."""

    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.data = data


class RefreshRequest(Message):
    """Request immediate refresh."""

    pass