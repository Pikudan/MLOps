# pyright: reportMissingImports=false

from pathlib import Path

from PIL import Image
import pytest
import torch
from torchvision.datasets import ImageFolder

from training.classification.src import (
    TrainingConfig,
    build_dataset,
    build_transforms,
    create_dataloaders,
    ensure_directory_structure,
    load_imagefolder_dataset,
    validate_batch,
    BatchValidationError,
)


def test_create_dataloaders_fake_dataset() -> None:
    cfg = TrainingConfig()
    cfg.data.dataset = "fake"
    cfg.data.train_size = 20
    cfg.data.val_size = 10
    cfg.data.num_classes = 3

    train_loader, val_loader = create_dataloaders(cfg.data, batch_size=4)

    images, labels = next(iter(train_loader))
    assert images.shape[0] == 4
    assert images.shape[1:] == torch.Size([3, cfg.data.image_size, cfg.data.image_size])
    assert labels.min().item() >= 0
    assert labels.max().item() < cfg.data.num_classes

    assert sum(batch[0].size(0) for batch in val_loader) == cfg.data.val_size


def test_imagefolder_raises_for_missing_path(tmp_path: Path) -> None:
    cfg = TrainingConfig()
    cfg.data.dataset = "imagefolder"
    cfg.data.train_dir = tmp_path / "train"
    cfg.data.val_dir = tmp_path / "val"

    with pytest.raises(FileNotFoundError):
        create_dataloaders(cfg.data, batch_size=4)


def test_build_transforms_returns_compose() -> None:
    cfg = TrainingConfig()
    cfg.data.augmentations["rotation"] = 5
    transform = build_transforms(cfg.data, train=True)
    sample = Image.new("RGB", (cfg.data.image_size, cfg.data.image_size))
    transformed = transform(sample)
    assert transformed.shape == (3, cfg.data.image_size, cfg.data.image_size)


def test_ensure_directory_structure_valid(tmp_path: Path) -> None:
    (tmp_path / "class_a").mkdir()
    (tmp_path / "class_a" / "img.jpg").write_bytes(b"fake")
    (tmp_path / "class_b").mkdir()
    (tmp_path / "class_b" / "img.jpg").write_bytes(b"fake")

    ensure_directory_structure(tmp_path)


def test_ensure_directory_structure_invalid(tmp_path: Path) -> None:
    (tmp_path / "class_a").mkdir()
    with pytest.raises(ValueError):
        ensure_directory_structure(tmp_path)


def test_load_imagefolder_dataset(tmp_path: Path) -> None:
    class_dir = tmp_path / "healthy"
    class_dir.mkdir(parents=True)
    image_path = class_dir / "sample.png"
    Image.new("RGB", (4, 4)).save(image_path)

    dataset = load_imagefolder_dataset(tmp_path, build_transforms(TrainingConfig().data, train=False))
    assert isinstance(dataset, ImageFolder)
    assert dataset.classes == ["healthy"]


def test_validate_batch_checks_ranges() -> None:
    images = torch.randn(4, 3, 32, 32)
    labels = torch.tensor([0, 1, 2, 1], dtype=torch.int64)
    validate_batch((images, labels), num_classes=3)

    bad_labels = torch.tensor([0, 4, 2, 1], dtype=torch.int64)
    with pytest.raises(BatchValidationError):
        validate_batch((images, bad_labels), num_classes=3)

