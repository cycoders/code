from pathlib import Path
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Dict, List, Set, Any, Tuple


def parse_coverage_xml(path: Path) -> Dict[str, Dict[str, Set[int]]]:
    """Parse a single coverage XML file into file -> coverage sets."""
    tree = ET.parse(path)
    root = tree.getroot()
    data: Dict[str, Dict[str, Set[int]]] = {}
    for package in root.findall(".//package"):
        for cls in package.findall("classes/class"):
            fname: str = cls.get("filename", "")
            if not fname:
                continue
            file_data = data.setdefault(fname, {
                "covered_lines": set(),
                "possible_lines": set(),
                "covered_branches": set(),
                "possible_branches": set(),
            })
            for line in cls.findall("lines/line"):
                num_str = line.get("number")
                if num_str is None:
                    continue
                num = int(num_str)
                hits_str = line.get("hits", "0")
                hits = int(hits_str)
                is_branch = line.get("branch") == "true"
                file_data["possible_lines"].add(num)
                if hits >= 1:
                    file_data["covered_lines"].add(num)
                if is_branch:
                    file_data["possible_branches"].add(num)
                    if hits >= 1:
                        file_data["covered_branches"].add(num)
    return data


def merge_reports(inputs: List[Path]) -> Dict[str, Dict[str, Set[int]]]:
    """Merge multiple parsed reports by unioning sets."""
    merged = defaultdict(lambda: {
        "covered_lines": set(),
        "possible_lines": set(),
        "covered_branches": set(),
        "possible_branches": set(),
    })
    for path in inputs:
        if not path.exists():
            raise FileNotFoundError(f"Missing report: {path}")
        data = parse_coverage_xml(path)
        for fname, fdata in data.items():
            mdata = merged[fname]
            mdata["covered_lines"] |= fdata["covered_lines"]
            mdata["possible_lines"] |= fdata["possible_lines"]
            mdata["covered_branches"] |= fdata["covered_branches"]
            mdata["possible_branches"] |= fdata["possible_branches"]
    return dict(merged)


def compute_stats(merged_data: Dict[str, Dict[str, Set[int]]]) -> List[Dict[str, Any]]:
    """Compute stats dicts for visualization."""
    stats = []
    for fname, fdata in merged_data.items():
        pl = len(fdata["possible_lines"])
        cl = len(fdata["covered_lines"])
        pb = len(fdata["possible_branches"])
        cb = len(fdata["covered_branches"])
        line_pct = (cl / pl * 100) if pl else 0.0
        branch_pct = (cb / pb * 100) if pb else None
        missed_lines = pl - cl
        stats.append({
            "file": fname,
            "line_pct": line_pct,
            "branch_pct": branch_pct,
            "missed_lines": missed_lines,
            "possible_lines": pl,
            "covered_lines": cl,
        })
    return sorted(stats, key=lambda s: s["line_pct"])  # Worst first


def write_xml(merged_data: Dict[str, Dict[str, Set[int]]], output: Path) -> None:
    """Write merged data back to coverage XML format."""
    root = ET.Element("coverage")
    sources = ET.SubElement(root, "sources")
    ET.SubElement(sources, "source").text = "."
    packages = ET.SubElement(root, "packages")
    package = ET.SubElement(packages, "package", name="")
    classes = ET.SubElement(package, "classes")
    for fname, fdata in sorted(merged_data.items()):
        pl = len(fdata["possible_lines"])
        cl = len(fdata["covered_lines"])
        pb = len(fdata["possible_branches"])
        cb = len(fdata["covered_branches"])
        line_rate = f"{cl / pl * 100:.2f}" if pl else "0"
        branch_rate = f"{cb / pb * 100:.2f}" if pb else "0"
        cls = ET.SubElement(
            classes,
            "class",
            filename=fname,
            lines=str(pl),
            line_rates=line_rate,
            branches=str(pb),
            branch_rates=branch_rate,
        )
        lines_el = ET.SubElement(cls, "lines")
        all_lines = sorted(fdata["possible_lines"])
        for num in all_lines:
            hits = "1" if num in fdata["covered_lines"] else "0"
            branch = num in fdata["possible_branches"]
            line_el = ET.SubElement(lines_el, "line", number=str(num), hits=hits)
            if branch:
                line_el.set("branch", "true")
    tree = ET.ElementTree(root)
    tree.write(output, encoding="utf-8", xml_declaration=True)
