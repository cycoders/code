__version__ = "0.1.0"

__title__ = "ab-test-calculator-cli"
__summary__ = "Production-grade CLI for A/B test design and analysis"

try:
    from importlib.metadata import version, PackageNotFoundError

    __version__ = version(__name__)
except PackageNotFoundError:
    pass  # package not installed