from cache_policy_advisor.parser import parse_combined

def test_parse_combined():
    line = '127.0.0.1 - - [10/Oct/2020:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 1234'
    assert parse_combined(line)['status'] == 200