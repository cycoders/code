from typing import Dict

from jinja2 import Environment, PackageLoader, select_autoescape

from .detector import INSTALL_CMDS  # For type hint


env = Environment(
    loader=PackageLoader("smart_readme_generator"),
    autoescape=select_autoescape(["md", "html", "xml"]),
    lstrip_blocks=True,
    trim_blocks=True,
)
template = env.get_template("readme.md.jinja")


def render_readme(data: Dict) -> str:
    """Render the README from detected data."""
    return template.render(**data)
