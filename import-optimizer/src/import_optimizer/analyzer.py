import libcst as cst


def get_provided_names(
    node: cst.Import | cst.ImportFrom,
) -> set[str]:
    """
    Extract local names provided by an import statement.
    """
    if isinstance(node, cst.Import):
        return {
            alias.asname.value if alias.asname else alias.name.value
            for alias in node.names
        }
    elif isinstance(node, cst.ImportFrom):
        if node.star_import:
            return {"__all__star__"}
        return {
            alias.asname.value if alias.asname else alias.name.value
            for alias in node.names
        }
    raise ValueError(f"Unexpected node: {node}")


class LoadedNamesVisitor(cst.CSTVisitor):
    """
    Collects all loaded name identifiers (simple static usage tracking).
    """

    def __init__(self) -> None:
        self.loaded: set[str] = set()

    def visit_Name(self, node: cst.Name) -> None:
        if isinstance(node.ctx, cst.Load):
            self.loaded.add(node.value)