from typosquat_auditor.formatters import format_output

def test_text_format():
    out = format_output([{'pair': ('foo', 'fooo'), 'score': 0.9}], 'text')
    assert 'foo ~ fooo' in out