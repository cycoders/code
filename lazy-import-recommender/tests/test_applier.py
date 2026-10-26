from lazy_import_recommender.applier import apply_changes

def test_dry_run(capsys, tmp_path):
    apply_changes(str(tmp_path), False)
    captured = capsys.readouterr()
    assert 'Dry-run' in captured.out