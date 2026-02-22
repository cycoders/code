class ExpansionError(Exception):
    """Base exception for expansion errors."""


class UndefinedVariable(ExpansionError):
    """Raised when a referenced variable is undefined."""


class CycleDetected(ExpansionError):
    """Raised when a cycle is detected in variable references."""