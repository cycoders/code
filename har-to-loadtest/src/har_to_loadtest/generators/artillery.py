from jinja2 import Template

from .base import Generator
from har_to_loadtest.model import HttpRequest


class ArtilleryGenerator(Generator):
    """Artillery YAML load test generator."""

    def generate(self) -> str:
        host = self._host()
        template_str = """config:
  target: "https://{{ host }}"
  phases:
    - duration: {{ duration }}
      arrivalRate: {{ (vus * 0.1)|round(1) }}
  engines:
    http:
      timeout: 10s

scenarios:
  - name: "HAR Replay"
    flowSequence:
      - think: {{ think_time }}
{% for req in requests %}
      - requests:
        - method: {{ req.method }}
          url: "{{ req.url }}"
        {%- if req.json_body or req.body %}
          {%- if req.json_body %}
          json:
            {{ req.json_body | tojson | indent(12) }}
          {%- else %}
          body: "{{ req.body }}"
          {%- endif %}
        {%- endif %}
          headers:
          {%- for name, value in req.headers.items() %}
            {{ name | title }}: "{{ value }}"
          {%- endfor %}
{% endfor %}
"""
        t = Template(template_str, trim_blocks=True)
        return t.render(
            requests=self.requests,
            host=host,
            vus=self.vus,
            duration=self.duration,
            think_time=self.think_time,
        )
