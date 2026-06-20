from benchstat_cli.parser import parse_file
import tempfile, json

def test_json_parse():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({'benchmarks': [{'name': 'foo', 'ns_per_op': 123}]}, f)
        f.flush()
        data = parse_file(f.name)
        assert data['benchmarks'][0]['name'] == 'foo'