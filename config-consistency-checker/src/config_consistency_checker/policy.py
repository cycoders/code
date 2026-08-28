import jsonschema

def validate_policy(config, schema):
    jsonschema.validate(config, schema)
    return True