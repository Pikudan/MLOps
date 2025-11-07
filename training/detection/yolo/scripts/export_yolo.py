"""Export trained YOLO model to multiple formats."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Optional

from ultralytics import YOLO


LOGGER = logging.getLogger("yolo-export")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export YOLO model to target format")
    parser.add_argument("weights", type=Path, help="Path to trained weights (e.g., best.pt)")
    parser.add_argument("--formats", nargs="*", default=["onnx"], help="Export formats")
    parser.add_argument("--output", type=Path, default=Path("training/models/yolo"), help="Output directory")
    parser.add_argument("--device", type=str, default="cpu", help="Device for export")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    return parser.parse_args(argv)


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def export(weights: Path, formats: list[str], output_dir: Path, device: str) -> None:
    if not weights.exists():
        raise FileNotFoundError(f"Weights not found: {weights}")

    model = YOLO(str(weights))
    output_dir.mkdir(parents=True, exist_ok=True)

    for fmt in formats:
        LOGGER.info("Exporting to %s", fmt)
        model.export(format=fmt, path=output_dir, device=device)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv)
    setup_logging(args.verbose)
    export(args.weights, args.formats, args.output, args.device)


if __name__ == "__main__":
    main()

