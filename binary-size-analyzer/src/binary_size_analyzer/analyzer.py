import lief
from typing import Dict, List, Any, NamedTuple


class SectionData(NamedTuple):
    name: str
    disk_size: int
    disk_pct: float
    mem_size: int
    mem_pct: float
    symbols_count: int


class SymbolData(NamedTuple):
    name: str
    size: int
    pct: float
    section: str


class LibData(NamedTuple):
    name: str


def analyze_binary(path: str) -> Dict[str, Any]:
    """
    Parse binary and extract size data.

    Returns dict with 'overall', 'sections', 'symbols', 'libs'.

    Raises ValueError if invalid binary.
    """
    binary = lief.parse(path)
    if binary is None:
        raise ValueError("Unsupported or invalid binary format")

    sections = binary.sections
    total_disk = sum(s.size for s in sections)
    total_mem = sum(s.virtual_size for s in sections)

    sections_data: List[SectionData] = []
    symbols_data: List[SymbolData] = []

    for sec in sections:
        sec_name = sec.name if sec.name else "<anon>"
        disk_pct = (sec.size / total_disk * 100) if total_disk > 0 else 0.0
        mem_pct = (sec.virtual_size / total_mem * 100) if total_mem > 0 else 0.0
        sym_count = len(sec.symbols)

        sections_data.append(
            SectionData(
                sec_name, sec.size, disk_pct, sec.virtual_size, mem_pct, sym_count
            )
        )

        # Extract sized symbols (funcs/vars)
        for sym in sec.symbols:
            if sym.size > 0:
                sym_pct = (sym.size / total_mem * 100) if total_mem > 0 else 0.0
                symbols_data.append(
                    SymbolData(sym.name or "<anon>", sym.size, sym_pct, sec_name)
                )

    # Sort sections by disk size
    sections_data = sorted(sections_data, key=lambda s: s.disk_size, reverse=True)
    # Sort symbols globally by size
    symbols_data = sorted(symbols_data, key=lambda s: s.size, reverse=True)

    libs = getattr(binary, "libraries", [])
    libs_data = [LibData(lib) for lib in libs]

    overall = {
        "format": str(binary.format).upper(),
        "architecture": str(getattr(binary.header, "machine", "unknown")),
        "total_disk_bytes": total_disk,
        "total_mem_bytes": total_mem,
        "sections_count": len(sections),
        "libs_count": len(libs),
    }

    return {
        "overall": overall,
        "sections": [s._asdict() for s in sections_data],
        "symbols": [s._asdict() for s in symbols_data],
        "libs": [l._asdict() for l in libs_data],
    }