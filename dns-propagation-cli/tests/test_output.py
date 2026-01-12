import io
from dns_propagation_cli.output import print_propagation_table, print_json, print_csv
from dns_propagation_cli.models import PropagationResult, Status


sample_results = [
    PropagationResult("Google", "8.8.8.8", "US", Status.PROPAGATED, "93.184.216.34", 42),
    PropagationResult("Cloudflare", "1.1.1.1", "Global", Status.PENDING, "old.ip", 28),
]


def test_print_json(capsys):
    print_json(sample_results)
    captured = capsys.readouterr()
    assert '"resolver_name": "Google"' in captured.out
    assert '"status": "✅ Propagated"' in captured.out


def test_print_csv(capsys):
    print_csv(sample_results)
    captured = capsys.readouterr()
    assert "resolver_name,ip,location,status,response-laten" in captured.out
    assert "Google,8.8.8.8,US,✅ Propagated,93.184.216.34," in captured.out
