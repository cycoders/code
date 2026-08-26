import json
import jsonschema
from jsonschema import ValidationError

def validate_stream(stream, schema_path):
    with open(schema_path) as s:
        schema = json.load(s)
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for lineno, line in enumerate(stream, 1):
        try:
            obj = json.loads(line)
            for err in validator.iter_errors(obj):
                errors.append({'line': lineno, 'path': list(err.path), 'message': err.message})
        except json.JSONDecodeError as e:
            errors.append({'line': lineno, 'path': [], 'message': str(e)})
    return errors