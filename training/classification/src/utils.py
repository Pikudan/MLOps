"""Helper utilities for training pipeline."""

from __future__ import annotations

import logging
import random
from pathlib import Path
from typing import Iterable, List, Sequence

import numpy as np
import torch

from .config import LoggingConfig
from .validation import validate_class_names, validate_probability_tensor


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


def logits_to_probabilities(logits: torch.Tensor) -> torch.Tensor:
    """Convert raw logits to probability distribution via softmax."""

    if logits.ndim == 1:
        logits = logits.unsqueeze(0)
    return torch.softmax(logits, dim=-1)


def probabilities_to_predictions(
    probs: torch.Tensor,
    class_names: Sequence[str] | None = None,
) -> List[dict]:
    """Convert probabilities to predicted class labels.

    Returns list of dictionaries with ``label`` and ``score`` keys for each sample.
    """

    if probs.ndim == 1:
        probs = probs.unsqueeze(0)

    validate_probability_tensor(probs)

    num_classes = probs.size(-1)

    if class_names is not None:
        validate_class_names(class_names, num_classes)

    top_scores, top_indices = torch.max(probs, dim=-1)

    predictions = []
    for score, idx in zip(top_scores.tolist(), top_indices.tolist()):
        label = class_names[idx] if class_names else idx
        predictions.append({"label": label, "score": float(score)})
    return predictions

