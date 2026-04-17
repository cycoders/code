import os
import math
import lief
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

from .utils import entropy, human_size, hex_addr


class BinaryAnalyzer:
    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        self.binary = lief.parse(self.path)
        if self.binary is None:
            raise ValueError(f"Invalid binary format: {path}")

    @property
    def format(self) -> str:
        return self.binary.format.name

    @property
    def architecture(self) -> str:
        try:
            machine = self.binary.header.machine
            arch_map = {
                lief.MACHINE_TYPES.I386: "i386",
                lief.MACHINE_TYPES.X86_64: "x86_64",
                lief.MACHINE_TYPES.ARM: "arm",
                lief.MACHINE_TYPES.AARCH64: "aarch64",
                lief.MACHINE_TYPES.PPC64: "ppc64",
            }
            return arch_map.get(machine, f"unknown({machine.value})")
        except AttributeError:
            return "unknown"

    @property
    def entrypoint(self) -> int:
        return self.binary.header.entrypoint

    @property
    def file_size_human(self) -> str:
        return human_size(os.path.getsize(self.path))

    @property
    def libraries(self) -> List[str):
        return self.binary.libraries

    @property
    def sections(self) -> List[Dict[str, Any]]:
        sections = []
        for s in self.binary.sections:
            sections.append({
                "name": s.name,
                "va": getattr(s, 'virtual_address', None),
                "size": s.size,
                "size_human": human_size(s.size),
                "entropy": entropy(s.content),
            })
        return sections

    @property
    def symbol_rows(self) -> List[Tuple[str, str, str]]:
        rows = []
        for sym in self.binary.symbols[:500]:  # limit perf
            name = sym.name or "<unnamed>"
            value = hex_addr(sym.value)
            size = human_size(sym.size) if sym.size else ""
            rows.append((name, value, size))
        return rows

    @property
    def strings(self) -> List[str]:
        return list(self.binary.strings(5))[:1000]
