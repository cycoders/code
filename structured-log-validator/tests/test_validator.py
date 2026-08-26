import pytest
from io import StringIO
from structured_log_validator.validator import validate_stream

def test_valid_line():
    schema = '{"type":"object","properties":{"level":{"type":"string"}}}'
    data = StringIO('{"level":"info"}\n')
    assert validate_stream(data, schema) == []

def test_missing_field():
    schema = '{"type":"object","required":["level"]}'
    data = StringIO('{"msg":"hi"}\n')
    errs = validate_stream(data, schema)
    assert len(errs) == 1 and 'required' in errs[0]['message']

def test_invalid_json():
    schema = '{}'
    data = StringIO('not json\n')
    errs = validate_stream(data, schema)
    assert 'Expecting value' in errs[0]['message']

def test_multiple_errors():
    schema = '{"type":"object","required":["a","b"]}'
    data = StringIO('{"a":1}\n{"b":2}\n')
    assert len(validate_stream(data, schema)) == 2

def test_nested_path():
    schema = '{"type":"object","properties":{"meta":{"type":"object","required":["id"]}}}'
    data = StringIO('{"meta":{}}\n')
    errs = validate_stream(data, schema)
    assert errs[0]['path'] == ['meta']