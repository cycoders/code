__version__ = "0.1.0"

from .cli import app

if __name__ == "__main__":
    import sys
    app(prog_name="sbom-generator-cli")