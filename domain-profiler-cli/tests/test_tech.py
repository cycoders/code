from src.domain_profiler_cli.profilers.tech import detect_tech


def test_tech_detection():
    headers = {"server": "nginx"}
    html = None
    techs = detect_tech(headers, html)
    assert any(t["name"] == "Nginx" for t in techs)


def test_no_tech():
    headers = {"server": "unknown"}
    html = ""
    techs = detect_tech(headers, html)
    assert len(techs) == 0