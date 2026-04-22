import pytest
from pathlib import Path

from arch_boundary_auditor.config import Config, Layer


@pytest.fixture
def sample_config_dict():
    return {
        "layers": [
            {"name": "domain", "package_prefixes": ["domain."], "allowed_layers": ["utils"], "forbidden_layers": ["infra"]},
            {"name": "infra", "package_prefixes": ["infra."], "allowed_layers": ["domain"]},
        ],
        "src_dir": "src",
        "allow_third_party": True,
    }


def test_load_config(tmp_path: Path, sample_config_dict):
    config_path = tmp_path / "boundaries.yaml"
    with open(config_path, "w") as f:
        import yaml
        yaml.safe_dump(sample_config_dict, f)

    config = Config.load(config_path)
    assert len(config.layers) == 2
    assert config.layers[0].name == "domain"
    assert config.allow_third_party is True


def test_invalid_config(tmp_path: Path):
    config_path = tmp_path / "boundaries.yaml"
    with open(config_path, "w") as f:
        f.write("invalid: yaml")

    with pytest.raises(ValueError):
        Config.load(config_path)