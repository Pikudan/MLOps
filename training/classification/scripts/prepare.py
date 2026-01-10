"""Data preparation script for DVC pipeline."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from collections import Counter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
LOGGER = logging.getLogger(__name__)


def count_images_in_directory(directory: Path) -> dict:
    """Count images per class in an ImageFolder-style directory."""
    class_counts = {}
    if not directory.exists():
        return class_counts
    
    for class_dir in sorted(directory.iterdir()):
        if class_dir.is_dir():
            images = list(class_dir.glob("*.JPG")) + list(class_dir.glob("*.jpg")) + \
                     list(class_dir.glob("*.png")) + list(class_dir.glob("*.jpeg"))
            class_counts[class_dir.name] = len(images)
    
    return class_counts


def prepare_dataset(data_dir: Path, output_file: Path) -> dict:
    """Prepare dataset and generate summary statistics."""
    
    LOGGER.info("Preparing dataset from: %s", data_dir)
    
    train_dir = data_dir / "train"
    val_dir = data_dir / "val"
    test_dir = data_dir / "test"
    
    summary = {
        "data_dir": str(data_dir),
        "splits": {}
    }
    
    for split_name, split_dir in [("train", train_dir), ("val", val_dir), ("test", test_dir)]:
        if split_dir.exists():
            class_counts = count_images_in_directory(split_dir)
            total = sum(class_counts.values())
            summary["splits"][split_name] = {
                "total_images": total,
                "num_classes": len(class_counts),
                "class_distribution": class_counts
            }
            LOGGER.info("%s split: %d images in %d classes", split_name, total, len(class_counts))
        else:
            LOGGER.warning("Split directory not found: %s", split_dir)
    
    # Extract class names from train split
    if "train" in summary["splits"]:
        summary["classes"] = list(summary["splits"]["train"]["class_distribution"].keys())
        summary["num_classes"] = len(summary["classes"])
    
    # Save summary
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    LOGGER.info("Dataset summary saved to: %s", output_file)
    
    return summary


def main():
    parser = argparse.ArgumentParser(description="Prepare dataset for training")
    parser.add_argument("--data-dir", type=Path, required=True, help="Path to dataset directory")
    parser.add_argument("--output", type=Path, default=Path("data_summary.json"), help="Output summary file")
    args = parser.parse_args()
    
    prepare_dataset(args.data_dir, args.output)


if __name__ == "__main__":
    main()

