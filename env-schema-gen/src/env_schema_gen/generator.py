'''
Generators for Pydantic models, docs, .env.example.
'''

from typing import Dict


def generate_pydantic_model(vars_info: Dict) -> str:
    """Generate Pydantic BaseModel str."""
    fields = []
    for var_name in sorted(vars_info['vars']):
        info = vars_info['vars'][var_name]
        typ_str = info['type']

        if typ_str == 'str':
            df = f"lambda: os.getenv('{var_name}')"
        elif typ_str == 'int':
            df = f"lambda: int(os.getenv('{var_name}', '0'))"
        elif typ_str == 'float':
            df = f"lambda: float(os.getenv('{var_name}', '0.0'))"
        elif typ_str == 'bool':
            df = f"lambda: os.getenv('{var_name}', 'false').lower() in ('true', '1', 'yes', 'on')"
        else:
            df = f"lambda: os.getenv('{var_name}')"
            typ_str = 'str'

        fields.append(f"    {var_name}: {typ_str} = Field(default_factory={df})\n")

    return f"""import os\nfrom pydantic import BaseModel, Field\n\nclass EnvSettings(BaseModel):\n{''.join(fields)}"""


def generate_docs(vars_info: Dict) -> str:
    """Generate Markdown table."""
    md = '# Environment Variables\n\n'
    md += f'**Total vars: {vars_info["summary"]["total_vars"]}**\n\n'
    md += '| Variable | Type | Locations |\n'
    md += '|----------|------|-----------|\n'
    for var_name in sorted(vars_info['vars']):
        info = vars_info['vars'][var_name]
        locs_str = ', '.join(
            f'`{f}:{l}`' for f, l in sorted(info['locations'])[:5]
        )
        if len(info['locations']) > 5:
            locs_str += ' ...'
        md += f'| `{var_name}` | `{info["type"]}` | {locs_str} |\n'
    return md


def generate_env_example(vars_info: Dict) -> str:
    """Generate .env.example."""
    lines = ['# Auto-generated .env.example from codebase scan\n\n']
    for var_name in sorted(vars_info['vars']):
        info = vars_info['vars'][var_name]
        default_ex = {
            'int': '0',
            'float': '0.0',
            'bool': 'false',
        }.get(info['type'], '')
        lines.append(f'{var_name}={default_ex}\n')
        files_used = '; '.join(set(f for f, _ in info['locations']))
        lines.append(f'# Used in: {files_used}\n\n')
    return ''.join(lines)