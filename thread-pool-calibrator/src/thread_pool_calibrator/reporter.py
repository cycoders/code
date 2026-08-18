from rich.table import Table

def render_recommendation(result):
    table = Table(title="Recommendation")
    table.add_column("Pool Size")
    table.add_row(str(result.get("optimal", 8)))
    return table