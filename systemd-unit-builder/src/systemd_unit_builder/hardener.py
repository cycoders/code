from .models import ServiceConfig

def apply_hardening(cfg: ServiceConfig) -> dict:
    unit = {
        "Description": cfg.name,
        "After": " ".join(cfg.after) if cfg.after else None,
        "Wants": " ".join(cfg.wants) if cfg.wants else None,
    }
    service = {
        "ExecStart": cfg.exec_start,
        "User": cfg.user,
        "WorkingDirectory": cfg.working_directory,
        "Environment": [f"{k}={v}" for k, v in cfg.environment.items()],
        "Restart": cfg.restart,
        "RestartSec": cfg.restart_sec,
        "PrivateTmp": "true" if cfg.private_tmp else "false",
        "NoNewPrivileges": "true" if cfg.no_new_privileges else "false",
    }
    return {"Unit": unit, "Service": service}