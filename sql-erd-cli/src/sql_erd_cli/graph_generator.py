import graphviz

from sql_erd_cli.models import Schema


def generate_erd(schema: Schema, layout: str = "dot") -> graphviz.Digraph:
    dot = graphviz.Digraph(
        graph_attr={"rankdir": "TB", "splines": "ortho", "layout": layout},
        node_attr={"shape": "record", "style": "filled", "fillcolor": "lightblue"},
    )
    dot.engine = layout

    for table_name, table in schema.tables.items():
        col_lines = []
        for col in table.columns.values():
            label = f"{col.name}: {col.type_}"
            if col.pk:
                label += " <b>PK</b>"
            if col.fkey:
                label += f" → {col.fkey}"
            col_lines.append(label)
        label = f"{{ <table> <b>{table_name}</b> | { ' | '.join(col_lines) } }}"
        dot.node(table_name, label=label)

        # FK edges
        for col in table.columns.values():
            if col.fkey:
                target_table = col.fkey.split('.')[0]
                dot.edge(table_name, target_table, label=col.name, color="blue", fontsize="10")

    return dot