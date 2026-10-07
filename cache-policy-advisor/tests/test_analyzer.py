from cache_policy_advisor.analyzer import analyze_logs

def test_analyze_empty(tmp_path):
    f = tmp_path / 'empty.log'
    f.write_text('')
    assert analyze_logs(f, None, '1d')['hit_rate'] == 0