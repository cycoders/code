from jinja2 import Template

from .base import Generator
from har_to_loadtest.model import HttpRequest


class LocustGenerator(Generator):
    """Locust Python load test generator."""

    def generate(self) -> str:
        template_str = """from locust import HttpUser, task, between

class HarUser(HttpUser):
    wait_time = between(1, 5)

{% for req in requests %}
    @task({{ (100 // requests|length) }})
    def task_{{ loop.index0 }}(self):
        headers = {
        {%- for name, value in req.headers.items() %}
            "{{ name }}": "{{ value }}",
        {%- endfor %}
        }
        {%- if req.json_body %}
        self.client.{{ req.method.lower() }}("{{ req.url }}", json={{ req.json_body | tojson }}, headers=headers)
        {%- elif req.body %}
        self.client.{{ req.method.lower() }}("{{ req.url }}", data="{{ req.body }}", headers=headers)
        {%- else %}
        self.client.{{ req.method.lower() }}("{{ req.url }}", headers=headers)
        {%- endif %}
{% endfor %}
"""
        t = Template(template_str, trim_blocks=True)
        return t.render(
            requests=self.requests,
            vus=self.vus,
            duration=self.duration,
            think_time=self.think_time,
        )
