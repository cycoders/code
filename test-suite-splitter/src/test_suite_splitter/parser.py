from __future__ import annotations

from pathlib import Path
from typing import Iterator, List

import lxml.etree as etree
from rich.progress import track

from .models import TestCase


def iter_junit_paths(paths: list[Path]) -> Iterator[Path]:
    """Yield all JUnit XML files from given paths (files/dirs)."""
    for path in paths:
        if path.is_dir():
            for p in path.rglob("*.xml"):
                if p.match("TEST*.xml") or p.name.endswith((".junit.xml", ".junit")):
                    yield p
        elif path.exists():
            yield path


def parse_junit(path: Path) -> list[TestCase]:
    """Parse a single JUnit XML file into TestCase list."""
    tree = etree.parse(str(path))
    tests: list[TestCase] = []
    for testcase in tree.xpath("//testcase"):
        suite = testcase.getparent().get("classname", "unknown")
        name = testcase.get("name", "unknown")
        try:
            duration = float(testcase.get("time", "0"))
        except ValueError:
            duration = 0.0
        tests.append(TestCase(suite=suite, name=name, duration=duration))
    return tests


def parse_junit_files(paths: list[Path]) -> list[TestCase]:
    """Parse all JUnit files from paths into flat TestCase list."""
    all_tests: list[TestCase] = []
    junit_paths = list(iter_junit_paths(paths))
    for path in track(junit_paths, description="Parsing XML"):
        all_tests.extend(parse_junit(path))
    return all_tests