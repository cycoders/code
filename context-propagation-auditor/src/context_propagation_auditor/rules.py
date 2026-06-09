import libcst as cst

class Finding:
    def __init__(self, path, line, message):
        self.path, self.line, self.message = path, line, message

class PropagationRule:
    DANGEROUS = {"create_task", "submit", "map"}
    def check(self, node: cst.Call):
        if isinstance(node.func, cst.Attribute) and node.func.attr.value in self.DANGEROUS:
            if not any(kw.arg == "context" for kw in node.keywords):
                return Finding("", node.lineno, "missing context copy")
        return None