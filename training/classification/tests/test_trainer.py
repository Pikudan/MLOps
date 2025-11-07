# pyright: reportMissingImports=false

import pytest
import torch
from torch.utils.data import DataLoader, TensorDataset

from training.classification.src import (
    BatchValidationError,
    Trainer,
    TrainingConfig,
    build_model,
    create_dataloaders,
)


def test_training_pipeline_runs_one_epoch() -> None:
    cfg = TrainingConfig()
    cfg.data.dataset = "fake"
    cfg.data.train_size = 30
    cfg.data.val_size = 10
    cfg.data.num_classes = 3
    cfg.optim.batch_size = 5
    cfg.optim.epochs = 1
    cfg.optim.device = "cpu"
    cfg.model.num_classes = 3

    train_loader, val_loader = create_dataloaders(cfg.data, batch_size=cfg.optim.batch_size)
    model = build_model(cfg.model)

    trainer = Trainer(model, cfg.optim, torch.device("cpu"))
    best_metrics, last_metrics = trainer.fit(train_loader, val_loader, epochs=cfg.optim.epochs)

    assert "val_accuracy" in last_metrics
    assert 0.0 <= last_metrics["val_accuracy"] <= 1.0
    assert best_metrics["val_accuracy"] >= 0.0


def test_trainer_validates_batches() -> None:
    cfg = TrainingConfig()
    cfg.data.dataset = "fake"
    cfg.data.train_size = 4
    cfg.data.val_size = 4
    cfg.data.num_classes = 3
    cfg.model.num_classes = 3
    cfg.optim.batch_size = 4
    cfg.optim.device = "cpu"

    model = build_model(cfg.model)
    trainer = Trainer(model, cfg.optim, torch.device("cpu"))

    images = torch.randn(4, 3, cfg.data.image_size, cfg.data.image_size)
    labels = torch.tensor([0, 1, 5, 1], dtype=torch.int64)
    loader = DataLoader(TensorDataset(images, labels), batch_size=4)

    with pytest.raises(BatchValidationError):
        trainer.train_epoch(loader)

