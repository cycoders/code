from rich.table import Table

def render_findings(findings):
    table = Table(title='N+1 Findings')
    # populate table
    return table