from git_hooks_manager.validator import validate_config

def test_valid_schema():
    assert validate_config({"hooks": []}) is True