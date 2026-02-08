from typing import Dict, Any, List

DEFAULT_SERVICES: Dict[str, Dict[str, Any]] = {
    "postgres": {
        "image": "postgres:16-alpine",
        "container_ports": ["5432"],
        "volumes": ["postgres_data:/var/lib/postgresql/data"],
        "environment": {
            "POSTGRES_DB": "dev",
            "POSTGRES_USER": "dev",
            "POSTGRES_PASSWORD": "devpass",
        },
        "healthcheck": {
            "test": ["CMD-SHELL", "pg_isready -U dev"],
            "interval": "10s",
            "timeout": "5s",
            "retries": 5,
        },
        "env_vars": {
            "DATABASE_URL": "postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{port_5432}/{POSTGRES_DB}",
        },
        "connect_cmd": ["psql", "-U", "dev", "-d", "dev"],
    },
    "redis": {
        "image": "redis:7-alpine",
        "container_ports": ["6379"],
        "volumes": ["redis_data:/data"],
        "healthcheck": {
            "test": ["CMD", "redis-cli", "ping"],
            "interval": "10s",
            "timeout": "5s",
            "retries": 5,
        },
        "env_vars": {
            "REDIS_URL": "redis://localhost:{port_6379}",
        },
        "connect_cmd": ["redis-cli"],
    },
    "minio": {
        "image": "minio/minio:latest",
        "container_ports": ["9000", "9001"],
        "volumes": ["minio_data:/data"],
        "environment": {
            "MINIO_ROOT_USER": "minioadmin",
            "MINIO_ROOT_PASSWORD": "minioadmin",
        },
        "command": "server /data --console-address ':9001'",
        "healthcheck": {
            "test": ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"],
            "interval": "30s",
            "timeout": "20s",
            "retries": 3,
        },
        "env_vars": {
            "S3_ENDPOINT": "http://localhost:{port_9000}",
            "S3_ACCESS_KEY": "{MINIO_ROOT_USER}",
            "S3_SECRET_KEY": "{MINIO_ROOT_PASSWORD}",
            "MINIO_CONSOLE": "http://localhost:{port_9001}",
        },
        # No connect_cmd - use browser for console
    },
}
