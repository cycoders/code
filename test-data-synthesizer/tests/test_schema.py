from test_data_synthesizer.schema import SchemaParser

def test_parse_json_schema():
    p = SchemaParser()
    assert p.parse('{"type":"object"}') == []