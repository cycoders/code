import xml.etree.ElementTree as ET
from pathlib import Path
import pytest
from coverage_merger.merger import parse_coverage_xml


@pytest.fixture
def sample_xml1(tmp_path: Path) -> Path:
    xml_content = '''
<?xml version="1.0" ?>
<coverage>
  <sources version="2">
    <source>/tmp</source>
  </sources>
  <packages>
    <package name="src">
      <classes>
        <class filename="file.py" lines="3" line_rates="66.67" branches="1" branch_rates="100.0">
          <lines>
            <line number="1" hits="1"/>
            <line number="2" hits="0"/>
            <line number="3" hits="1" branch="true"/>
          </lines>
        </class>
      </classes>
    </package>
  </packages>
</coverage>
'''
    p = tmp_path / "report1.xml"
    p.write_text(xml_content)
    return p


@pytest.fixture
def sample_xml2(tmp_path: Path) -> Path:
    xml_content = '''
<?xml version="1.0" ?>
<coverage>
  <sources version="2">
    <source>/tmp</source>
  </sources>
  <packages>
    <package name="src">
      <classes>
        <class filename="file.py" lines="2" line_rates="50.0" branches="0">
          <lines>
            <line number="2" hits="1"/>
            <line number="4" hits="0"/>
          </lines>
        </class>
      </classes>
    </package>
  </packages>
</coverage>
'''
    p = tmp_path / "report2.xml"
    p.write_text(xml_content)
    return p
