"""Entry point for training models with MLflow integration."""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional
import json

import torch
import mlflow
import mlflow.pytorch

from .src.config import load_config
from .src.data import create_dataloaders, describe_dataset
from .src.model import build_model
from .src.trainer import Trainer
from .src.utils import set_seed, setup_logging

LOGGER = logging.getLogger(__name__)


def get_dvc_hash() -> str:
    """Get hash of current DVC data version."""
    try:
        dvc_file = Path("training/classification/datasets/tomato.dvc")
        if dvc_file.exists():
            import yaml
            with open(dvc_file, "r") as f:
                dvc_data = yaml.safe_load(f)
            return dvc_data.get("outs", [{}])[0].get("md5", "unknown")
    except Exception as e:
        LOGGER.warning("Could not get DVC hash: %s", e)
    return "unknown"


def get_git_commit() -> str:
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()[:8]
    except Exception:
        return "unknown"


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train image classification model")
    parser.add_argument("config", type=Path, help="Path to YAML config file")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument("--epochs", type=int, help="Override number of epochs")
    parser.add_argument("--batch-size", type=int, help="Override batch size")
    parser.add_argument("--experiment-name", type=str, default="tomato-disease-classification", 
                        help="MLflow experiment name")
    parser.add_argument("--run-name", type=str, default=None, help="MLflow run name")
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

    # Set MLflow tracking URI (local by default)
    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "mlruns")
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    
    # Set experiment
    mlflow.set_experiment(args.experiment_name)
    
    # Start MLflow run
    run_name = args.run_name or f"train-{get_git_commit()}"
    
    with mlflow.start_run(run_name=run_name):
        LOGGER.info("Started MLflow run: %s", mlflow.active_run().info.run_id)
        
        # Log parameters
        mlflow.log_params({
            "seed": cfg.seed,
            "model_architecture": cfg.model.architecture,
            "hidden_dim": cfg.model.hidden_dim,
            "num_classes": cfg.model.num_classes,
            "dropout": cfg.model.dropout,
            "learning_rate": cfg.optim.learning_rate,
            "weight_decay": cfg.optim.weight_decay,
            "epochs": cfg.optim.epochs,
            "batch_size": cfg.optim.batch_size,
            "device": cfg.optim.device,
            "image_size": cfg.data.image_size,
        })
        
        # Log DVC tags for data versioning
        dvc_hash = get_dvc_hash()
        git_commit = get_git_commit()
        mlflow.set_tags({
            "dvc_data_hash": dvc_hash,
            "git_commit": git_commit,
            "config_file": str(args.config),
        })
        LOGGER.info("DVC data hash: %s", dvc_hash)
        
        # Create dataloaders
        train_loader, val_loader = create_dataloaders(cfg.data, batch_size=cfg.optim.batch_size)
        dataset_info = describe_dataset(train_loader)
        
        # Log dataset info
        mlflow.log_param("train_samples", dataset_info.get("samples", 0))
        
        # Build model and trainer
        device = torch.device(cfg.optim.device if torch.cuda.is_available() or cfg.optim.device == "cpu" else "cpu")
        model = build_model(cfg.model)
        trainer = Trainer(model, cfg.optim, device)
        
        # Training with metric logging
        best_metrics, last_metrics = trainer.fit(train_loader, val_loader, epochs=cfg.optim.epochs)
        
        # Log final metrics
        for key, value in best_metrics.items():
            mlflow.log_metric(f"best_{key}", value)
        for key, value in last_metrics.items():
            mlflow.log_metric(f"last_{key}", value)
        
        LOGGER.info("Best metrics: %s", best_metrics)
        LOGGER.info("Last metrics: %s", last_metrics)
        
        # Save model
        if cfg.save.output_dir:
            output_dir = Path(cfg.save.output_dir)
            model.save_pretrained(output_dir)
            LOGGER.info("Model saved to %s", output_dir)
            
            # Log model as MLflow artifact
            mlflow.pytorch.log_model(
                model, 
                "model",
                registered_model_name="tomato-disease-classifier"
            )
            
            # Log model config as artifact
            config_artifact = output_dir / "config.json"
            if config_artifact.exists():
                mlflow.log_artifact(str(config_artifact), "model_config")
        
        # Log dvc.lock as artifact if exists
        dvc_lock_path = Path("dvc.lock")
        if dvc_lock_path.exists():
            mlflow.log_artifact(str(dvc_lock_path), "dvc")
            LOGGER.info("Logged dvc.lock as artifact")
        
        # Log config file as artifact
        mlflow.log_artifact(str(args.config), "config")
        
        LOGGER.info("MLflow run completed: %s", mlflow.active_run().info.run_id)


if __name__ == "__main__":
    main()
