from log_schema_inferrer.generator import generate_parser
import tempfile, os

def test_generates_valid_python():
    schema = {"fields": {"ts": {"type": "datetime"}}}
    with tempfile.TemporaryDirectory() as tmp:
        generate_parser(schema, tmp)
        assert (os.path.join(tmp, "generated_parser.py")).exists()