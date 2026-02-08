import json
from unittest.mock import patch, MagicMock
from local_service_hub.manager import (
    generate_compose,
    get_effective_services,
    get_ports_map,
    print_env,
    status,
)


@patch("local_service_hub.manager.run_docker")
@patch("local_service_hub.manager.Console.print")
def test_status(mock_print, mock_docker):
    mock_docker.return_value.stdout = json.dumps([{"Name": "lsh-app_postgres_1", "Status": "Up healthy", "Ports": "0.0.0.0:1234->5432/tcp"}])
    status()
    mock_print.assert_called()

@patch("subprocess.check_output")
def test_get_ports_map(mock_output):
    mock_output.return_value = b"0.0.0.0:49152->5432/tcp\n"
    ports = get_ports_map("postgres", ["5432"])
    assert ports["5432"] == "49152"

@patch("local_service_hub.config.load_config")
def test_effective_services(mock_load):
    mock_load.return_value = {"services": {"postgres": {"enabled": False}}}
    svcs = get_effective_services()
    assert "postgres" not in svcs

# More: generate_compose requires jinja/filesystem
