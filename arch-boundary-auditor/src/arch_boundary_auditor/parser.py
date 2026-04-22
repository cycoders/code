import libcst as cst
from typing import List, Tuple


def extract_imports(code: str) -> List[Tuple[str, int]]:
    """
    Extract absolute import module names and their start lines.
    Skips relative imports.
    """
    tree = cst.parse_module(code)
    wrapper = cst.MetadataWrapper(tree)

    class ImportVisitor(cst.CSTVisitor):
        METADATA_DEPENDENCIES = (cst.PositionProvider,)

        def __init__(self):
            super().__init__()
            self.imports: List[Tuple[str, int]] = []

        def visit_Import(self, node: cst.Import) -> None:
            if node.module:
                mod_name = get_full_module_name(node.module)
                self.imports.append((mod_name, node.start_line))
            self.generic_visit(node)

        def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
            if node.module and not node.relative:
                mod_name = get_full_module_name(node.module)
                self.imports.append((mod_name, node.start_line))
            self.generic_visit(node)

    visitor = ImportVisitor()
    wrapper.visit(visitor)
    return visitor.imports


def get_full_module_name(node: cst.BaseExpression) -> str:
    if isinstance(node, cst.Name):
        return node.value
    elif isinstance(node, cst.Attribute):
        return f"{get_full_module_name(node.value)}.{node.attr.value}"
    raise ValueError(f"Unsupported module node: {type(node).__name__}")