from jinja2 import Template
import json

def generate_report(results: dict, path: str):
    tpl = Template("...")  # production template
    html = tpl.render(results=results)
    with open(path, "w") as f:
        f.write(html)