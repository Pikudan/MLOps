from pathlib import Path

import pytest

import tests._import_src  # noqa: F401

from src.config import TrainingConfig, load_config, ConfigError  # type: ignore[import]


def test_load_config_from_yaml(tmp_path: Path) -> None:
    yaml_content = """
seed: 123
data:
  dataset: fake
model:
  num_classes: 4
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content, encoding="utf-8")

    config = load_config(config_file)
    assert config.seed == 123
    assert config.data.dataset == "fake"
    assert config.model.num_classes == 4


def test_missing_config_file() -> None:
    missing_path = Path("missing_config.yaml")
    with pytest.raises(ConfigError):
        TrainingConfig.from_yaml(missing_path)

