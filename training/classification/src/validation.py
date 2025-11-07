"""Validation utilities for datasets, batches and predictions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import torch


@dataclass(frozen=True)
class BatchValidationError(Exception):
    """Raised when a batch does not satisfy expected constraints."""

    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.message


def ensure_directory_structure(path: Path) -> None:
    """Ensure ``ImageFolder``-style structure exists under ``path``."""

    if not path.exists():
        raise FileNotFoundError(f"Dataset path does not exist: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Dataset path must be a directory: {path}")

    class_dirs = [p for p in path.iterdir() if p.is_dir()]
    if not class_dirs:
        raise ValueError(f"Dataset path {path} does not contain any class folders")

    for folder in class_dirs:
        has_images = any(child.is_file() for child in folder.iterdir())
        if not has_images:
            raise ValueError(f"Class folder {folder} does not contain any files")


def validate_image_tensor(images: torch.Tensor) -> None:
    if images.ndim != 4:
        raise BatchValidationError(f"Expected image batch with 4 dims, got shape {tuple(images.shape)}")
    if images.dtype not in (torch.float32, torch.float16):
        raise BatchValidationError(f"Images must be float tensors, got dtype={images.dtype}")
    if not torch.isfinite(images).all():
        raise BatchValidationError("Images contain NaN or Inf values")


def validate_label_tensor(labels: torch.Tensor, num_classes: int) -> None:
    if labels.ndim != 1:
        raise BatchValidationError(f"Expected 1D labels tensor, got shape {tuple(labels.shape)}")
    if labels.dtype not in (torch.int64, torch.int32):
        raise BatchValidationError(f"Labels must be integer tensor, got dtype={labels.dtype}")
    if labels.numel() == 0:
        raise BatchValidationError("Labels tensor is empty")
    if labels.min().item() < 0 or labels.max().item() >= num_classes:
        raise BatchValidationError(
            f"Labels must be within [0, {num_classes - 1}], got range "
            f"[{labels.min().item()}, {labels.max().item()}]"
        )


def validate_batch(batch: tuple[torch.Tensor, torch.Tensor], num_classes: int) -> None:
    images, labels = batch
    validate_image_tensor(images)
    validate_label_tensor(labels, num_classes)
    if images.size(0) != labels.size(0):
        raise BatchValidationError(
            f"Batch size mismatch between images ({images.size(0)}) and labels ({labels.size(0)})"
        )


def validate_probability_tensor(probs: torch.Tensor) -> None:
    if probs.ndim != 2:
        raise ValueError(f"Probabilities tensor must be 2D, got shape {tuple(probs.shape)}")
    if probs.size(-1) == 0:
        raise ValueError("Probabilities tensor has zero classes")
    if not torch.isfinite(probs).all():
        raise ValueError("Probabilities tensor contains NaN or Inf")
    row_sums = probs.sum(dim=-1)
    if not torch.allclose(row_sums, torch.ones_like(row_sums), atol=1e-3):
        raise ValueError("Probabilities rows must sum to 1 within tolerance")
    if (probs < 0).any() or (probs > 1).any():
        raise ValueError("Probabilities must be in the [0, 1] range")


def validate_class_names(class_names: Sequence[str], num_classes: int) -> None:
    if len(class_names) != num_classes:
        raise ValueError(
            f"Number of class names ({len(class_names)}) does not match number of classes ({num_classes})"
        )
    if len(set(class_names)) != len(class_names):
        raise ValueError("Class names must be unique")

