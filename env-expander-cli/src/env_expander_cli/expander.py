import re
from typing import Dict, Set
from .expander_errors import ExpansionError, UndefinedVariable, CycleDetected


class EnvExpander:
    def __init__(self, env: Dict[str, str]):
        self.env = env
        self.resolved: Dict[str, str] = {}
        self.visiting: Set[str] = set()

    def expand_all(self) -> Dict[str, str]:
        """Expand all variables recursively."""
        result: Dict[str, str] = {}
        for var in list(self.env):
            result[var] = self._expand_var(var)
        return result

    def _expand_var(self, var: str) -> str:
        if var in self.resolved:
            return self.resolved[var]
        if var not in self.env:
            raise UndefinedVariable(var)
        if var in self.visiting:
            raise CycleDetected(var)
        self.visiting.add(var)
        raw = self.env[var]
        expanded = self._interpolate(raw)
        self.visiting.remove(var)
        self.resolved[var] = expanded
        return expanded

    def _interpolate(self, value: str) -> str:
        pattern = re.compile(r'\$\{([^}:]+)(:?-)([^}]*)\}')

        def replacer(match: re.Match) -> str:
            varname = match.group(1)
            sep = match.group(2)
            default_str = match.group(3)
            try:
                expanded_var = self._expand_var(varname)
            except UndefinedVariable:
                if sep:
                    return self._interpolate(default_str)
                raise
            if sep == ':-' and not expanded_var:
                return self._interpolate(default_str)
            return expanded_var

        return pattern.sub(replacer, value)