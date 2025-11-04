# pyright: reportMissingImports=false

import tests._import_src  # type: ignore[import] # noqa: F401
import torch  # type: ignore[import]

from src.config import TrainingConfig  # type: ignore[import]
from src.data import create_dataloaders  # type: ignore[import]
from src.model import build_model  # type: ignore[import]
from src.trainer import Trainer  # type: ignore[import]


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

