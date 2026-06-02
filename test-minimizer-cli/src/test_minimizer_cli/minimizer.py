from __future__ import annotations
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Callable, List

class DeltaMinimizer:
    def __init__(self, test_cmd: Callable[[Path], bool], granularity: int = 2):
        self.test_cmd = test_cmd
        self.granularity = granularity

    def minimize(self, original: str) -> str:
        current = original
        while True:
            chunks = self._split(current)
            reduced = False
            for i, chunk in enumerate(chunks):
                candidate = ''.join(chunks[:i] + chunks[i+1:])
                if self.test_cmd(self._write_temp(candidate)):
                    current = candidate
                    reduced = True
                    break
            if not reduced:
                break
        return current

    def _split(self, text: str) -> List[str]:
        size = max(1, len(text) // self.granularity)
        return [text[i:i+size] for i in range(0, len(text), size)]

    def _write_temp(self, content: str) -> Path:
        tmp = Path(tempfile.mkdtemp())
        (tmp / "test_repro.py").write_text(content)
        return tmp