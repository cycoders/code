from test_impact_analyzer.analyzer import ImpactAnalyzer

ia = ImpactAnalyzer(".coverage")
print(ia.analyze("main", "HEAD"))