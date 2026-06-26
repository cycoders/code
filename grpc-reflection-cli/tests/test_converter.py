def test_to_openapi_minimal():
    assert "openapi" in __import__('grpc_reflection_cli.converter').converter.to_openapi({})