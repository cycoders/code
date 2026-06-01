# Architecture

1. Parse every .py file with Python's ast module
2. Visit With nodes that acquire known Lock objects
3. Record directed edges representing observed acquisition order
4. Run DFS-based cycle detection on the aggregated graph
5. Report minimal cycles with source locations

Edge cases handled: nested context managers, multiple acquire patterns, and files without threading usage.