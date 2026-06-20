import numpy as np

def compare(results, threshold=0.05):
    base, current = results[0], results[1]
    report = []
    for b1, b2 in zip(base['benchmarks'], current['benchmarks']):
        delta = (b2['ns_per_op'] - b1['ns_per_op']) / b1['ns_per_op']
        if abs(delta) > threshold:
            report.append(f"{b1['name']}: {delta:+.1%}")
    return '\n'.join(report) if report else 'No significant change'