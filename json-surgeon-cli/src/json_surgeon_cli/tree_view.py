from typing import Any, Union, List, TypedDict
from textual.widgets import Tree


JsonNodeData = TypedDict("JsonNodeData", {"path": List[Union[str, int]], "value": Any, "is_leaf": bool})


class JsonTree(Tree[JsonNodeData]):
    """Custom Tree for JSON with path tracking."""

    def load_tree(self, data: Any) -> None:
        """Load and build tree from JSON data."""
        self.clear()
        root = self.add("root", expand=True, data={"path": [], "value": data, "is_leaf": False})
        self._populate(root, data, [])

    def _populate(
        self, node: Tree.Node[JsonNodeData], data: Any, path: List[Union[str, int]]
    ) -> None:
        from .utils import get_summary

        node_data: JsonNodeData = {"path": path, "value": data, "is_leaf": True}

        if isinstance(data, (str, int, float, bool, type(None))):
            label = f"{path[-1] if path else 'root'}: {get_summary(data)}"
            node.label = label
            node.data = node_data
            return

        node_data["is_leaf"] = False
        label = f"{path[-1] if path else 'root'} {get_summary(data)}"
        node.label = label
        node.data = node_data

        if isinstance(data, dict):
            for key, val in data.items():
                child_path = path + [key]
                child = node.add_leaf(f"", data={"path": child_path[:], "value": val, "is_leaf": False})
                self._populate(child, val, child_path)
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                child_path = path + [idx]
                child = node.add_leaf("", data={"path": child_path[:], "value": item, "is_leaf": False})
                self._populate(child, item, child_path)

    def get_cursor_data(self) -> JsonNodeData | None:
        """Get data of focused node."""
        cursor_node = self.cursor_node
        return cursor_node.data if cursor_node else None