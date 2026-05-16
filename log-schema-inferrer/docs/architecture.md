# Architecture

1. Line sampling (first 1000 lines per file)
2. Pattern detection via regex + heuristics
3. Field frequency aggregation + confidence calculation
4. Code generation with safe templates

Error handling: malformed lines are skipped with warning logs.