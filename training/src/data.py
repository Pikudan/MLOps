"""Data loading and preprocessing utilities."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Tuple

from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms

from .config import DataConfig

LOGGER = logging.getLogger(__name__)


def _get_transforms(cfg: DataConfig, train: bool) -> transforms.Compose:
    resize = transforms.Resize((cfg.image_size, cfg.image_size))
    augmentations = []

    if train and cfg.augmentations.get("horizontal_flip", True):
        augmentations.append(transforms.RandomHorizontalFlip())
    if train and cfg.augmentations.get("rotation", 0) > 0:
        augmentations.append(transforms.RandomRotation(cfg.augmentations.get("rotation", 0)))

    augmentations.extend([transforms.ToTensor()])

    normalize = cfg.augmentations.get("normalize", None)
    if normalize:
        augmentations.append(
            transforms.Normalize(mean=normalize.get("mean", [0.485, 0.456, 0.406]),
                                 std=normalize.get("std", [0.229, 0.224, 0.225]))
        )

    return transforms.Compose([resize, *augmentations])


def _load_image_folder(path: Path, transform: transforms.Compose) -> Dataset:
    if not path or not path.exists():
        raise FileNotFoundError(f"Dataset path does not exist: {path}")
    return datasets.ImageFolder(root=str(path), transform=transform)


def _build_dataset(cfg: DataConfig, train: bool) -> Dataset:
    transform = _get_transforms(cfg, train=train)
    dataset_type = cfg.dataset.lower()

    if dataset_type == "imagefolder":
        directory = cfg.train_dir if train else cfg.val_dir
        if directory is None:
            raise ValueError("train_dir and val_dir must be provided for imagefolder dataset")
        return _load_image_folder(Path(directory), transform=transform)
    if dataset_type == "fake":
        return datasets.FakeData(
            size=cfg.train_size if train else cfg.val_size,
            image_size=(3, cfg.image_size, cfg.image_size),
            num_classes=cfg.num_classes,
            transform=transform,
        )
    raise ValueError(f"Unsupported dataset type: {cfg.dataset}")


def create_dataloaders(cfg: DataConfig, batch_size: int, num_workers: int = 0) -> Tuple[DataLoader, DataLoader]:
    """Create train and validation dataloaders."""

    LOGGER.info("Creating dataloaders using dataset=%s", cfg.dataset)

    train_dataset = _build_dataset(cfg, train=True)
    val_dataset = _build_dataset(cfg, train=False)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers or cfg.num_workers,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers or cfg.num_workers,
    )

    return train_loader, val_loader


def describe_dataset(loader: DataLoader) -> Dict[str, int]:
    """Return basic statistics for a dataloader."""

    count = 0
    label_histogram: Dict[int, int] = {}
    for _, target in loader:
        count += target.size(0)
        for label in target.tolist():
            label_histogram[label] = label_histogram.get(label, 0) + 1

    LOGGER.info("Dataset samples: %s", count)
    LOGGER.info("Label histogram: %s", label_histogram)
    return {"samples": count, "label_histogram": label_histogram}

