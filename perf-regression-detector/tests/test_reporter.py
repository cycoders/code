from perf_regression_detector.reporter import delta_pct, status_symbol


def test_delta_pct():
    assert delta_pct(10, 100) == 10.0
    assert delta_pct(90, 100) == -10.0


def test_status_symbol():
    assert status_symbol(6, 5) == "regression"
    assert status_symbol(-6, 5) == "improvement"
    assert status_symbol(2, 5) == "pass"