from pathlib import Path
import git
from radon.complexity import cc_visit

def analyze_hotspots(repo_path: str, since: str, top: int):
    repo = git.Repo(repo_path)
    churn = {}
    for commit in repo.iter_commits(since=since):
        for f in commit.stats.files:
            churn[f] = churn.get(f, 0) + 1
    results = []
    for path, changes in sorted(churn.items(), key=lambda x: -x[1])[:top*3]:
        if not path.endswith('.py'): continue
        try:
            code = Path(repo_path, path).read_text()
            complexity = sum(b.complexity for b in cc_visit(code))
            risk = round(complexity * (changes ** 0.7), 2)
            results.append({'path': path, 'churn': changes, 'complexity': complexity, 'risk': risk})
        except Exception:
            continue
    return sorted(results, key=lambda x: -x['risk'])[:top]