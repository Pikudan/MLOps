"""Utilities for reading and validating training configuration."""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class ConfigError(ValueError):
    """Raised when configuration is invalid."""


@dataclass
class DataConfig:
    dataset: str = "imagefolder"
    train_dir: Optional[Path] = None
    val_dir: Optional[Path] = None
    image_size: int = 224
    num_classes: int = 2
    train_size: int = 200
    val_size: int = 50
    num_workers: int = 0
    augmentations: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelConfig:
    architecture: str = "simple_cnn"
    in_channels: int = 3
    hidden_dim: int = 64
    num_classes: int = 2
    dropout: float = 0.3


@dataclass
class OptimConfig:
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    epochs: int = 5
    batch_size: int = 32
    device: str = "cpu"


@dataclass
class LoggingConfig:
    level: str = "INFO"
    log_dir: Path = Path("training/logs")
    log_to_file: bool = True


@dataclass
class SaveConfig:
    output_dir: Path = Path("training/models/latest")
    save_best: bool = True


@dataclass
class TrainingConfig:
    seed: int = 42
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    optim: OptimConfig = field(default_factory=OptimConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    save: SaveConfig = field(default_factory=SaveConfig)

    @classmethod
    def from_yaml(cls, path: Path) -> "TrainingConfig":
        """Create configuration from YAML file."""

        if not path.exists():
            raise ConfigError(f"Config file not found: {path}")

        with path.open("r", encoding="utf-8") as fp:
            data = yaml.safe_load(fp)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "TrainingConfig":
        """Construct configuration from dictionary."""

        if not isinstance(raw, dict):
            raise ConfigError("Configuration must be a dictionary")

        data_raw = dict(raw.get("data", {}))
        if data_raw.get("train_dir") is not None:
            data_raw["train_dir"] = Path(data_raw["train_dir"])
        if data_raw.get("val_dir") is not None:
            data_raw["val_dir"] = Path(data_raw["val_dir"])
        data_cfg = DataConfig(**data_raw)

        model_cfg = ModelConfig(**raw.get("model", {}))
        optim_cfg = OptimConfig(**raw.get("optim", {}))

        logging_raw = dict(raw.get("logging", {}))
        if logging_raw.get("log_dir") is not None:
            logging_raw["log_dir"] = Path(logging_raw["log_dir"])
        logging_cfg = LoggingConfig(**logging_raw)

        save_raw = dict(raw.get("save", {}))
        if save_raw.get("output_dir") is not None:
            save_raw["output_dir"] = Path(save_raw["output_dir"])
        save_cfg = SaveConfig(**save_raw)

        return cls(
            seed=raw.get("seed", 42),
            data=data_cfg,
            model=model_cfg,
            optim=optim_cfg,
            logging=logging_cfg,
            save=save_cfg,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as serializable dictionary."""

        def _serialize(obj: Any) -> Any:
            if dataclasses.is_dataclass(obj):
                return {k: _serialize(v) for k, v in dataclasses.asdict(obj).items()}
            if isinstance(obj, Path):
                return str(obj)
            if isinstance(obj, (list, tuple)):
                return [_serialize(item) for item in obj]
            return obj

        return _serialize(self)

    def save_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fp:
            json.dump(self.to_dict(), fp, indent=2, ensure_ascii=False)


def load_config(path: Path) -> TrainingConfig:
    return TrainingConfig.from_yaml(path)

