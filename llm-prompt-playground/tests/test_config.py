from llm_prompt_playground.config import load_config, Config


def test_load_config(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "http://test")
    config = load_config()
    assert config.base_url == "http://test"


def test_default_config(tmp_path):
    config = load_config()
    assert config.default_model == "gpt-4o-mini"
