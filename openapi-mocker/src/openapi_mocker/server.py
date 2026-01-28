import logging
from pathlib import Path
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .mock_generator import generate_mock
from .spec_parser import load_spec
from .types import OpenAPISpec

logger = logging.getLogger(__name__)


_METHODS = ['get', 'post', 'put', 'delete', 'patch']


def create_mock_app(spec_path: Path, cors_origins: List[str]) -> FastAPI:
    """
    Create FastAPI app with dynamic routes from OpenAPI spec.

    Args:
        spec_path: Path to spec file.
        cors_origins: Allowed CORS origins.

    Returns:
        Configured FastAPI instance.
    """
    spec: OpenAPISpec = load_spec(spec_path)

    app = FastAPI(
        title="OpenAPI Mocker",
        description="Mock server generated from OpenAPI spec",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    # CORS
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info(f"CORS enabled for: {', '.join(cors_origins)}")

    # Dynamic routes
    route_count = 0
    for path_str, path_item in spec.paths.items():
        for method in _METHODS:
            op: Optional[OpenAPISpec] = getattr(path_item, method)
            if not op:
                continue

            # Default to 200 or first success code
            resp_code = next((k for k in op.responses if k.startswith('2')), None)
            if not resp_code:
                logger.debug(f"Skipping {method} {path_str}: no 2xx response")
                continue

            resp = op.responses[resp_code]
            content = resp.content.get('application/json', {})
            response_schema = content.get('schema', {'type': 'object'})

            async def make_handler(schema=response_schema, p=path_str, m=method):
                async def handler(request: Request) -> JSONResponse:
                    mock_data = generate_mock(schema)
                    logger.info(f"Mock {m.upper()} {p} -> {len(str(mock_data))} bytes")
                    return JSONResponse(content=mock_data)
                return handler

            app.add_api_route(path_str, make_handler(), methods=[method], include_in_schema=False)
            route_count += 1

    logger.info(f"Registered {route_count} mock routes")

    @app.get('/health')
    async def health_check():
        return {'status': 'healthy', 'routes': route_count}

    return app