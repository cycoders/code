import json

from postman_auditor_cli.models import Collection, ValidationError


def test_valid_parse():
    data = {
        "info": {"name": "test"},
        "item": [
            {
                "name": "req",
                "request": {
                    "method": "GET",
                    "url": {"raw": "https://example.com"}
                }
            }
        ],
    }
    coll = Collection.model_validate(data)
    assert coll.info["name"] == "test"
    assert len(coll.item) == 1


def test_invalid_schema():
    data = {"info": {}}
    with pytest.raises(ValidationError):
        Collection.model_validate(data)


def test_missing_name():
    data = {
        "info": {"name": "test"},
        "item": [{"request": {"method": "GET", "url": {"raw": ""}}},
    ]
    with pytest.raises(ValidationError, match="name"):
        Collection.model_validate(data)
