import pytest
from postman_auditor_cli.auditor import Auditor
from postman_auditor_cli.models import Collection
import json
from pathlib import Path


@pytest.fixture
def demo_collection():
    # Same as conftest but inline for isolation
    data = json.loads(Path(__file__).parent.parent.joinpath("../examples/demo.json").read_text())
    return Collection.model_validate(data)


def test_secrets_detection(demo_collection):
    issues = Auditor.audit(demo_collection)
    secret_issues = [i for i in issues if i.code.startswith("secret")]
    assert len(secret_issues) >= 4  # url, header x2, body


def test_unused_var(demo_collection):
    issues = Auditor.audit(demo_collection)
    unused = [i for i in issues if i.code == "unused-var"]
    assert len(unused) == 1
    assert "unused_var" in unused[0].message


def test_duplicates(demo_collection):
    issues = Auditor.auditor.Auditor.audit(demo_collection)
    dups = [i for i in issues if i.code == "duplicate-name"]
    assert len(dups) == 1
    assert "Get User" in dups[0].message


def test_no_desc(demo_collection):
    issues = Auditor.audit(demo_collection)
    descs = [i for i in issues if i.code == "no-folder-desc"]
    assert len(descs) == 1


def test_invalid_url(demo_collection):
    issues = Auditor.audit(demo_collection)
    urls = [i for i in issues if i.code == "invalid-url"]
    assert len(urls) == 1


def test_no_issues_empty():
    data = {
        "info": {"name": "clean"},
        "item": [
            {
                "name": "Clean",
                "description": "ok",
                "request": {"method": "GET", "url": {"raw": "https://ok.com"}},
                "auth": {"type": "bearer"},
            }
        ],
    }
    coll = Collection.model_validate(data)
    issues = Auditor.audit(coll)
    assert len(issues) == 0
