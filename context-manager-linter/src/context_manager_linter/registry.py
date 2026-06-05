from typing import Set

DEFAULT_RESOURCES: Set[str] = {
    "open", "file", "Lock", "RLock", "Semaphore", "BoundedSemaphore",
    "Event", "Condition", "sqlite3.connect", "Session", "requests.Session"
}