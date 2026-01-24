import json
import re
from typing import Any

from .models import PlanNode


def parse_explain(content: str, db: str = "auto") -> PlanNode:
    content = content.strip()
    lines = content.splitlines()

    if db != "auto":
        if db == "postgres":
            return parse_postgres(json.loads(content))
        elif db == "sqlite":
            return parse_sqlite(content)
        elif db == "mysql":
            return parse_mysql(json.loads(content))
        else:
            raise ValueError(f"Unsupported database: {db}")

    # Auto-detect
    if any("QUERY PLAN" in line for line in lines[:3]):
        return parse_sqlite(content)

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON or unrecognized SQLite format")

    data_str = str(data).lower()
    if "node type" in data_str or "plans" in data_str:
        return parse_postgres(data)
    elif "query_block" in data_str:
        return parse_mysql(data)
    else:
        raise ValueError("Unable to auto-detect format. Specify --db postgres|sqlite|mysql")


def parse_postgres(data: Any) -> PlanNode:
    if isinstance(data, list) and len(data) == 1:
        data = data[0]
    if isinstance(data, dict) and "Plan" in data:
        data = data["Plan"]

    node = PlanNode(
        node_type=data.get("Node Type", "Unknown"),
        startup_cost=data.get("Startup Cost"),
        total_cost=data.get("Total Cost"),
        plan_rows=data.get("Plan Rows"),
        plan_width=data.get("Plan Width"),
        actual_total_time=data.get("Actual Total Time"),
        actual_rows=data.get("Actual Rows"),
        actual_loops=data.get("Actual Loops"),
        children=[parse_postgres(child) for child in data.get("Plans", [])],
    )
    node.extra = {k: v for k, v in data.items() if k not in ["Plans", "Node Type", "Startup Cost", "Total Cost", "Plan Rows", "Plan Width", "Actual Total Time", "Actual Rows", "Actual Loops"]}
    return node


def parse_sqlite(content: str) -> PlanNode:
    lines = [line.rstrip() for line in content.splitlines() if line.strip()]
    if not lines or lines[0].strip() != "QUERY PLAN":
        raise ValueError("Invalid SQLite QUERY PLAN format")

    root = PlanNode(node_type="Query Plan")
    stack: list[PlanNode] = [root]

    for line in lines[1:]:
        # Parse tree prefix: count indent levels (~4 chars per level)
        prefix = re.match(r"^([ `|-]+)(.*)", line)
        if not prefix:
            continue
        prefix_chars, node_type = prefix.groups()
        level = len(prefix_chars) // 4

        node = PlanNode(node_type=node_type.strip())

        # Pop stack to correct level
        while len(stack) > level + 1:
            stack.pop()
        parent = stack[-1]
        parent.children.append(node)
        stack.append(node)

    return root.children[0] if root.children else root


def parse_mysql(data: dict) -> PlanNode:
    qb = data.get("query_block", {})
    node = PlanNode(
        node_type="Query Block",
        extra={"select_id": qb.get("select_id")}
    )

    def extract_node(d: dict) -> PlanNode:
        if "table" in d:
            table_info = d["table"]
            nt = f'{table_info.get("access_type", "table")} on {table_info.get("table_name", "?")}'
            extra = dict(table_info)
        else:
            nt = next(iter(d), "unknown")
            extra = dict(d)
        return PlanNode(node_type=nt, extra=extra)

    for key, val in qb.items():
        if isinstance(val, list):
            for item in val:
                node.children.append(extract_node(item))
        elif isinstance(val, dict) and key not in ["cost_info", "sorted_row_references"]:
            node.children.append(extract_node(val))

    return node