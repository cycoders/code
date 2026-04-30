import pytest
from pathlib import Path

from shell_auditor_cli.core import audit, parse_script
from shell_auditor_cli.types import Issue


@pytest.fixture
def bad_script():
    return """#!/bin/sh
eval foo
rm *
cat log | grep err
for i in $(ls); do echo $i; done
[[ $x == y ]]"""


def test_parse_script(tmp_path: Path):
    text = "echo hello"
    nodes = parse_script(text)
    assert len(nodes) == 1
    assert hasattr(nodes[0], "parts")


def test_audit_no_issues(bad_script):
    path = Path("good.sh")
    path.write_text("echo 'hello'")
    result = audit(path)
    assert len(result.issues) == 0


def test_detect_eval(bad_script):
    path = Path("test.sh")
    path.write_text(bad_script)
    result = audit(path)
    evals = [i for i in result.issues if i.rule_id == "SEC001"]
    assert len(evals) == 1
    assert evals[0].severity == "critical"


def test_perf_cat_pipeline(bad_script):
    path = Path("test.sh")
    path.write_text(bad_script)
    result = audit(path)
    cats = [i for i in result.issues if i.rule_id == "PERF001"]
    assert len(cats) == 1
    assert "grep err log" in cats[0].fix


def test_port_bashism(bad_script):
    path = Path("test.sh")
    path.write_text(bad_script)
    result = audit(path)
    ports = [i for i in result.issues if i.rule_id == "PORT001"]
    assert len(ports) >= 1


def test_parse_error():
    path = Path("invalid.sh")
    path.write_text("invalid syntax %%")
    result = audit(path)
    assert result.parse_errors
    assert len(result.issues) == 0