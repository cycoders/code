import xml.etree.ElementTree as ET
from pathlib import Path
import pytest

from test_suite_splitter.models import TestCase
from test_suite_splitter.parser import parse_junit
from test_suite_splitter.splitter import split_tests


@pytest.fixture
def sample_xml(tmp_path: Path) -> Path:
    """Single JUnit XML with nested suites."""
    path = tmp_path / "TEST-example.xml"
    tree = ET.Element("testsuites", name="sample", tests="5")
    slow_suite = ET.SubElement(tree, "testsuite", name="slow", tests="3", time="5.0")
    ET.SubElement(slow_suite, "testcase", name="slow1", classname="slow", time="2.5")
    ET.SubElement(slow_suite, "testcase", name="slow2", classname="slow", time="1.8")
    ET.SubElement(slow_suite, "testcase", name="slow3", classname="slow", time="0.7")
    fast_suite = ET.SubElement(tree, "testsuite", name="fast", tests="2", time="1.123")
    ET.SubElement(fast_suite, "testcase", name="fast1", classname="fast", time="0.6")
    ET.SubElement(fast_suite, "testcase", name="fast2", classname="fast", time="0.523")
    path.write_bytes(ET.tostring(tree, encoding="utf-8", xml_declaration=True))
    return path


@pytest.fixture
def empty_xml(tmp_path: Path) -> Path:
    path = tmp_path / "empty.xml"
    path.write_text("<testsuites></testsuites>")
    return path


@pytest.fixture
def invalid_xml(tmp_path: Path) -> Path:
    path = tmp_path / "invalid.xml"
    path.write_text("<invalid>bad</invalid>")
    return path