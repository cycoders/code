OPTIMIZATION_HINTS = {
    'LOAD_GLOBAL': 'Consider using a local binding',
    'FOR_ITER': 'Vectorized path available in 3.12+'}

def suggest_optimizations(instructions):
    return [OPTIMIZATION_HINTS.get(i.opname, '') for i in instructions if i.opname in OPTIMIZATION_HINTS]