"""CLI script for training YOLO models using Ultralytics API."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from ultralytics import YOLO


LOGGER = logging.getLogger("yolo-train")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train YOLO model from YAML config")
    parser.add_argument("config", type=Path, help="Path to YAML configuration")
    parser.add_argument("--epochs", type=int, help="Override number of epochs")
    parser.add_argument("--batch", type=int, help="Override batch size")
    parser.add_argument("--device", type=str, help="Override device string (e.g., 'cpu', '0')")
    parser.add_argument("--dry-run", action="store_true", help="Load config and model without training")
    parser.add_argument("--verbose", action="store_true", help="Enable DEBUG logging")
    return parser.parse_args(argv)


def setup_logging(logging_cfg: Dict[str, Any]) -> None:
    level = logging_cfg.get("level", "INFO")
    handlers = [logging.StreamHandler()]

    if logging_cfg.get("log_to_file", False):
        log_dir = Path(logging_cfg.get("log_dir", "training/logs/yolo"))
        log_dir.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_dir / "train.log", encoding="utf-8"))

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def load_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    with path.open("r", encoding="utf-8") as fp:
        cfg: Dict[str, Any] = yaml.safe_load(fp)
    return cfg


def apply_overrides(cfg: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    if args.epochs:
        cfg.setdefault("data", {})["epochs"] = args.epochs
    if args.batch:
        cfg.setdefault("data", {})["batch"] = args.batch
    if args.device:
        cfg.setdefault("data", {})["device"] = args.device
    if args.verbose:
        cfg.setdefault("logging", {})["level"] = "DEBUG"
    return cfg


def train(cfg: Dict[str, Any], dry_run: bool = False) -> None:
    model_weights = cfg.get("model", {}).get("weights", "yolov8n.pt")
    data_cfg = cfg.get("data", {})

    LOGGER.info("Loading YOLO model from %s", model_weights)
    model = YOLO(model_weights)

    if dry_run:
        LOGGER.info("Dry run enabled: skipping training")
        return

    LOGGER.info("Training with configuration: %s", data_cfg)
    results = model.train(**data_cfg)
    LOGGER.info("Training completed. Metrics: %s", getattr(results, "results_dict", {}))

    if cfg.get("save", {}).get("save_pretrained", True):
        output_dir = Path(cfg.get("save", {}).get("output_dir", "training/models/yolo"))
        output_dir.mkdir(parents=True, exist_ok=True)
        LOGGER.info("Saving Ultralytics checkpoint to %s", output_dir)
        model.save(output_dir / "weights.pt")

        export_formats = cfg.get("save", {}).get("export_formats", [])
        for fmt in export_formats:
            LOGGER.info("Exporting model to %s", fmt)
            model.export(format=fmt, path=output_dir)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv)
    cfg = load_config(args.config)
    cfg = apply_overrides(cfg, args)

    setup_logging(cfg.get("logging", {}))
    LOGGER.info("Loaded config from %s", args.config)

    train(cfg, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

