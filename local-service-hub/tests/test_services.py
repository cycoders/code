from local_service_hub.services import DEFAULT_SERVICES


def test_default_services():
    assert "postgres" in DEFAULT_SERVICES
    assert DEFAULT_SERVICES["postgres"]["container_ports"] == ["5432"]
    assert "env_vars" in DEFAULT_SERVICES["postgres"]


def test_env_vars_format():
    pg = DEFAULT_SERVICES["postgres"]
    format_dict = {
        "POSTGRES_USER": "dev",
        "POSTGRES_PASSWORD": "devpass",
        "POSTGRES_DB": "dev",
        "port_5432": "49152",
    }
    url = pg["env_vars"]["DATABASE_URL"].format(**format_dict)
    assert url == "postgres://dev:devpass@localhost:49152/dev"
