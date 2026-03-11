from jinja2 import Template

from .base import Generator
from har_to_loadtest.model import HttpRequest


class K6Generator(Generator):
    """k6 JavaScript load test generator."""

    def generate(self) -> str:
        template_str = """import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
    vus: {{ vus }},
    duration: '{{ duration }}',
};

export default function () {
{% for req in requests %}
    http.{{ req.method.lower() }}('{{ req.url }}'{% if req.body or req.json_body %}, 
        {%- if req.json_body %}JSON.stringify({{ req.json_body | tojson }}){%- elif req.body %}'{{ req.body | e }}'{%- endif %}, 
        { 
        {%- for header_name, header_value in req.headers.items() %}
            '{{ header_name }}': '{{ header_value | e }}'{% if not loop.last %},{% endif %}
        {%- endfor %}
        }{% endif %});
{% endfor %}
    sleep({{ think_time }});
}
"""
        t = Template(template_str, trim_blocks=True)
        return t.render(
            requests=self.requests,
            vus=self.vus,
            duration=self.duration,
            think_time=self.think_time,
        )
