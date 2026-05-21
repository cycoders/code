from code_hotspot_detector.core import analyze_hotspots
results = analyze_hotspots('.', '90d', 10)
print(results[:3])