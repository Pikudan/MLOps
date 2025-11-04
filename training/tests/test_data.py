from pathlib import Path

import pytest
import torch

from src.config import TrainingConfig
from src.data import create_dataloaders


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

