import json
import logging
import threading
from pathlib import Path
from typing import Any, Callable, Dict

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)

class ConfigReloader:
    def __init__(self, path: str | Path, validator: Callable[[Dict[str, Any]], None] | None = None):
        self.path = Path(path).resolve()
        self.validator = validator or (lambda c: None)
        self._config: Dict[str, Any] = {}
        self._lock = threading.RWLock() if hasattr(threading, 'RWLock') else threading.RLock()
        self._observer = Observer()
        self._load()

    def _load(self) -> None:
        try:
            data = yaml.safe_load(self.path.read_text()) or {}
            self.validator(data)
            with self._lock:
                self._config = data
            logger.info("Config loaded successfully")
        except Exception as exc:
            logger.exception("Failed to load config: %s", exc)
            raise

    @property
    def current(self) -> Dict[str, Any]:
        with self._lock:
            return self._config.copy()

    def __enter__(self):
        handler = FileSystemEventHandler()
        handler.on_modified = lambda e: self._load() if e.src_path == str(self.path) else None
        self._observer.schedule(handler, str(self.path.parent), recursive=False)
        self._observer.start()
        return self

    def __exit__(self, *exc):
        self._observer.stop()
        self._observer.join()