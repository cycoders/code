from pathlib import Path
import yaml
import numpy as np

def simulate(rules_dir: str, metrics_path: str, since: str):
    rules = list(Path(rules_dir).glob("*.yaml"))
    results = []
    for rule_file in rules:
        rule = yaml.safe_load(rule_file.read_text())
        # Placeholder for real PromQL evaluation + time series replay
        results.append({"rule": rule.get("alert"), "firings": 0})
    return results