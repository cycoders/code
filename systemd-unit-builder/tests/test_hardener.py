from systemd_unit_builder.hardener import apply_hardening
from systemd_unit_builder.models import ServiceConfig

def test_hardening_flags():
    cfg = ServiceConfig(name="x", exec_start="/bin/true")
    data = apply_hardening(cfg)
    assert data["Service"]["PrivateTmp"] == "true"
    assert data["Service"]["NoNewPrivileges"] == "true"