import pytest
from port_scanner_cli.services import identify_service


def test_identify_service_known_port_banner():
    assert identify_service(22, "OpenSSH_9.3p1") == "SSH (openssh)"
    assert identify_service(80, "Server: nginx/1.25.3") == "HTTP (nginx)"
    assert identify_service(3306, "5.7.44-1ubuntu") == "MySQL (mysql)"


def test_identify_service_no_match():
    assert identify_service(22, "Custom SSH") == "SSH"
    assert identify_service(9999, "Random") == "unknown"


def test_identify_case_insensitive():
    assert identify_service(80, "APACHE/2.4") == "HTTP (apache)"