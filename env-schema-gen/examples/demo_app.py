# Demo app showcasing detected patterns

import os

# Direct getenv with str default
DB_HOST = os.getenv('DB_HOST', 'localhost')

# Required
API_KEY = os.environ['API_KEY']

# Typed int
def get_port():
    return int(os.getenv('PORT', '8000'))

# Bool from get
DEBUG = bool(os.environ.get('DEBUG', False))

# Float
METRIC_SCALE = float(os.getenv('SCALE', '1.0'))

# Inside lambda (pydantic-like)
def active_factory():
    return os.getenv('USER_ACTIVE', 'true').lower() == 'true'

print('Run: env-schema-gen generate .')