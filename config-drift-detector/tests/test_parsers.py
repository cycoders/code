from config_drift_detector.parsers import load

def test_yaml(tmp_path):
    p = tmp_path / 'a.yaml'
    p.write_text('key: value')
    assert load(p)['key'] == 'value'