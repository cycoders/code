import pytest
from pydantic import ValidationError
from link_metadata_cli.models import Metadata


def test_metadata_model():
    data = {
        "url": "https://test.com",
        "title": "Test",
        "description": "Desc",
        "image": "https://test.com/img.jpg",
        "site_name": "Site",
        "type": "website",
        "raw": {},
    }
    meta = Metadata(**data)
    assert meta.title == "Test"
    assert meta.model_dump() == data


def test_metadata_partial():
    data = {"url": "https://test.com"}
    meta = Metadata(**data)
    assert meta.title is None


def test_metadata_extra_forbidden():
    data = {"url": "https://test.com", "extra": "invalid"}
    with pytest.raises(ValidationError):
        Metadata(**data)
