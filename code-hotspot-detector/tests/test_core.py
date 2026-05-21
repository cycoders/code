import tempfile
import git
from code_hotspot_detector.core import analyze_hotspots

def test_basic_analysis():
    with tempfile.TemporaryDirectory() as tmp:
        repo = git.Repo.init(tmp)
        f = tmp + '/a.py'
        open(f, 'w').write('def f():\n    if True: pass\n')
        repo.index.add(['a.py'])
        repo.index.commit('initial')
        res = analyze_hotspots(tmp, '1d', 5)
        assert len(res) == 1
        assert res[0]['churn'] == 1