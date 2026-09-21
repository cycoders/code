import json

def format_output(findings, fmt):
    if fmt == 'json':
        return json.dumps(findings, indent=2)
    if fmt == 'sarif':
        return '{"version":"2.1.0","runs":[{"tool":{"driver":{"name":"typosquat-auditor"}},"results":[]}]}'
    return '\n'.join(f"{f['pair'][0]} ~ {f['pair'][1]} ({f['score']})" for f in findings) or 'No suspicious pairs found.'