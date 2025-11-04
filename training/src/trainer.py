"""Training loop utilities."""

from __future__ import annotations

import logging
from typing import Dict, Tuple

import torch
from torch import nn
from torch.optim import AdamW
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from .config import OptimConfig

LOGGER = logging.getLogger(__name__)


class Trainer:
    def __init__(
        self,
        model: nn.Module,
        optim_cfg: OptimConfig,
        device: torch.device,
    ) -> None:
        self.model = model.to(device)
        self.optim_cfg = optim_cfg
        self.device = device

        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = AdamW(
            self.model.parameters(),
            lr=optim_cfg.learning_rate,
            weight_decay=optim_cfg.weight_decay,
        )

    def train_epoch(self, loader: DataLoader) -> Dict[str, float]:
        self.model.train()
        epoch_loss = 0.0
        correct = 0
        total = 0

        for batch in tqdm(loader, desc="Training", leave=False):
            inputs, targets = batch
            inputs, targets = inputs.to(self.device), targets.to(self.device)

            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = self.criterion(outputs, targets)
            loss.backward()
            self.optimizer.step()

            epoch_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, dim=1)
            correct += (preds == targets).sum().item()
            total += targets.size(0)

        avg_loss = epoch_loss / total
        accuracy = correct / total if total > 0 else 0.0
        return {"train_loss": avg_loss, "train_accuracy": accuracy}

    @torch.no_grad()
    def evaluate(self, loader: DataLoader) -> Dict[str, float]:
        self.model.eval()
        epoch_loss = 0.0
        correct = 0
        total = 0

        for inputs, targets in loader:
            inputs, targets = inputs.to(self.device), targets.to(self.device)
            outputs = self.model(inputs)
            loss = self.criterion(outputs, targets)

            epoch_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, dim=1)
            correct += (preds == targets).sum().item()
            total += targets.size(0)

        avg_loss = epoch_loss / total if total > 0 else 0.0
        accuracy = correct / total if total > 0 else 0.0
        return {"val_loss": avg_loss, "val_accuracy": accuracy}

    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int,
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        best_metrics: Dict[str, float] = {}
        best_accuracy = 0.0

        for epoch in range(1, epochs + 1):
            LOGGER.info("Epoch %s/%s", epoch, epochs)
            train_metrics = self.train_epoch(train_loader)
            val_metrics = self.evaluate(val_loader)

            LOGGER.info("Train metrics: %s", train_metrics)
            LOGGER.info("Validation metrics: %s", val_metrics)

            if val_metrics.get("val_accuracy", 0.0) >= best_accuracy:
                best_accuracy = val_metrics.get("val_accuracy", 0.0)
                best_metrics = {**train_metrics, **val_metrics}

        return best_metrics, val_metrics

