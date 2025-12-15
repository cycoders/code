from env_schema_gen.generator import (
    generate_pydantic_model,
    generate_docs,
    generate_env_example,
)


SAMPLE_DATA = {
    'vars': {
        'DB_HOST': {'type': 'str', 'locations': [('app.py', 1)]},
        'PORT': {'type': 'int', 'locations': [('app.py', 2)]},
    },
    'summary': {'total_vars': 2},
}


def test_generate_pydantic_model():
    content = generate_pydantic_model(SAMPLE_DATA)
    assert 'DB_HOST' in content
    assert 'lambda: os.getenv' in content
    assert 'int(os.getenv' in content


def test_generate_docs():
    content = generate_docs(SAMPLE_DATA)
    assert '| DB_HOST | `str` |' in content


def test_generate_env_example():
    content = generate_env_example(SAMPLE_DATA)
    assert 'DB_HOST=' in content
    assert '# Used in: app.py' in content