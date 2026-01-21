"""CLI entrypoint for `python -m db_migration_auditor`."""

from .cli import app

if __name__ == "__main__":
    app(prog_name="db-migration-auditor")