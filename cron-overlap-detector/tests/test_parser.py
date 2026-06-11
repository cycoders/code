import tempfile
from cron_overlap_detector.parser import parse_crontab

def test_parse_simple():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('* * * * * /bin/true\n')
    assert len(parse_crontab(f.name)) == 1