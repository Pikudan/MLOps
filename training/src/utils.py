"""Helper utilities for training pipeline."""

from __future__ import annotations

import logging
import random
from pathlib import Path

import numpy as np
import torch

from .config import LoggingConfig


def setup_logging(cfg: LoggingConfig) -> None:
    handlers = [logging.StreamHandler()]
    if cfg.log_to_file:
        cfg.log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(cfg.log_dir / "training.log", encoding="utf-8")
        handlers.append(file_handler)

    logging.basicConfig(
        level=getattr(logging, cfg.level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

