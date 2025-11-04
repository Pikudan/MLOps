"""Entry point for training models."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Optional

import torch

from src.config import load_config
from src.data import create_dataloaders, describe_dataset
from src.model import build_model
from src.trainer import Trainer
from src.utils import set_seed, setup_logging

LOGGER = logging.getLogger(__name__)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train image classification model")
    parser.add_argument("config", type=Path, help="Path to YAML config file")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument("--epochs", type=int, help="Override number of epochs")
    parser.add_argument("--batch-size", type=int, help="Override batch size")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv)
    cfg = load_config(args.config)

    if args.epochs:
        cfg.optim.epochs = args.epochs
    if args.batch_size:
        cfg.optim.batch_size = args.batch_size

    if args.verbose:
        cfg.logging.level = "DEBUG"

    setup_logging(cfg.logging)
    LOGGER.info("Loaded config from %s", args.config)
    LOGGER.info("Configuration: %s", cfg.to_dict())

    set_seed(cfg.seed)

    train_loader, val_loader = create_dataloaders(cfg.data, batch_size=cfg.optim.batch_size)
    describe_dataset(train_loader)

    device = torch.device(cfg.optim.device if torch.cuda.is_available() or cfg.optim.device == "cpu" else "cpu")
    model = build_model(cfg.model)
    trainer = Trainer(model, cfg.optim, device)

    best_metrics, last_metrics = trainer.fit(train_loader, val_loader, epochs=cfg.optim.epochs)

    LOGGER.info("Best metrics: %s", best_metrics)
    LOGGER.info("Last metrics: %s", last_metrics)

    if cfg.save.output_dir:
        model.save_pretrained(cfg.save.output_dir)
        LOGGER.info("Model saved to %s", cfg.save.output_dir)


if __name__ == "__main__":
    main()

