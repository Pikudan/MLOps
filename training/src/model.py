"""Model definitions and saving utilities."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any

import torch
from torch import nn

from .config import ModelConfig

LOGGER = logging.getLogger(__name__)


class SimpleCNN(nn.Module):
    """Simple convolutional neural network for classification."""

    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        self.cfg = cfg
        hidden = cfg.hidden_dim
        num_classes = cfg.num_classes

        self.features = nn.Sequential(
            nn.Conv2d(cfg.in_channels, hidden, kernel_size=3, padding=1),
            nn.BatchNorm2d(hidden),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(hidden, hidden * 2, kernel_size=3, padding=1),
            nn.BatchNorm2d(hidden * 2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
        )

        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Dropout(cfg.dropout),
            nn.Linear(hidden * 2, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        return self.classifier(x)

    def save_pretrained(self, output_dir: Path) -> None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        weights_path = output_dir / "pytorch_model.bin"
        config_path = output_dir / "config.json"

        LOGGER.info("Saving model weights to %s", weights_path)
        torch.save(self.state_dict(), weights_path)

        LOGGER.info("Saving model config to %s", config_path)
        with config_path.open("w", encoding="utf-8") as fp:
            json.dump(asdict(self.cfg), fp, indent=2, ensure_ascii=False)

    @classmethod
    def from_pretrained(cls, directory: Path, map_location: str | None = None) -> "SimpleCNN":
        directory = Path(directory)
        config_path = directory / "config.json"
        weights_path = directory / "pytorch_model.bin"

        if not config_path.exists() or not weights_path.exists():
            raise FileNotFoundError("Pretrained model files not found")

        with config_path.open("r", encoding="utf-8") as fp:
            params: Dict[str, Any] = json.load(fp)

        cfg = ModelConfig(**params)
        model = cls(cfg)
        state_dict = torch.load(weights_path, map_location=map_location)
        model.load_state_dict(state_dict)
        return model


def build_model(cfg: ModelConfig) -> SimpleCNN:
    if cfg.architecture != "simple_cnn":
        raise ValueError(f"Unsupported architecture: {cfg.architecture}")
    return SimpleCNN(cfg)

