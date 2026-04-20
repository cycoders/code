from statistical_power_analyzer.power_analysis import compute_power_analysis

# Lib usage example
result = compute_power_analysis(
    test_type="ttest-ind",
    effect_size=0.3,
    power=0.9,
    solve_for="nobs"
)
print(result)

# {'test_type': 'ttest-ind', 'nobs1': 175.67, 'nobs2': 175.67, ...}
