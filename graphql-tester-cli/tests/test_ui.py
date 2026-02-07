from graphql_tester_cli.ui import render_result, render_history_list


def test_render_result_data(capsys):
    result = {"data": {"user": {"name": "Alice"}}, "extensions": {"trace": True}}
    render_result(result)
    captured = capsys.readouterr()
    assert "Data:" in captured.out
    assert '"user": {"name": "Alice"}' in captured.out


def test_render_result_errors(capsys):
    result = {"errors": [{"message": "Invalid id", "locations": [{"line": 1}]}]}
    render_result(result)
    captured = capsys.readouterr()
    assert "Errors:" in captured.out
    assert "Invalid id" in captured.out


def test_render_history_list(capsys):
    history = [
        {"id": 1, "endpoint": "https://api.com", "query": "{ user }", "timestamp": "2024-01-01"}
    ]
    render_history_list(history)
    captured = capsys.readouterr()
    assert "Recent Queries" in captured.out
