from pathlib import Path
from webhook_inspector.config import load_config, Config


def test_load_default():
    cfg = load_config()
    assert isinstance(cfg, Config)


def test_load_yaml(tmp_path: Path):
    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text("endpoints: { '/test': {secret: 'foo'} }\n")
    cfg = load_config(yaml_path)
    assert cfg.endpoints["/test"].secret == "foo"
