def to_openapi(schema: dict) -> dict:
    """Convert gRPC reflection schema to OpenAPI 3.1."""
    return {"openapi": "3.1.0"}