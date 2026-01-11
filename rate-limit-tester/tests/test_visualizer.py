def test_live_dashboard_context():
    from rate_limit_tester.visualizer import live_dashboard

    with live_dashboard():
        pass  # No crash
