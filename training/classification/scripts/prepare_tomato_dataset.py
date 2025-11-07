"""Utility to extract tomato disease dataset from PlantVillage collection."""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


TOMATO_MARKER = "Tomato___"


@dataclass(frozen=True)
class Sample:
    source: Path
    cls: str
    filename: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare tomato disease classification splits from PlantVillage dataset.",
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        required=True,
        help="Path to PlantVillage-Dataset root directory.",
    )
    parser.add_argument(
        "--target-root",
        type=Path,
        required=True,
        help="Directory to store prepared dataset (train/val/test).",
    )
    parser.add_argument(
        "--val-split",
        type=float,
        default=0.15,
        help="Fraction of training data to move to validation split (per class).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible splitting.",
    )
    parser.add_argument(
        "--use-symlinks",
        action="store_true",
        help="Create symbolic links instead of copying files.",
    )
    return parser.parse_args()


def read_mapping_file(path: Path) -> Iterable[Tuple[Path, str]]:
    with path.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line or "\t" not in line:
                continue
            src_rel, dst_rel = line.split("\t")
            yield Path(src_rel), dst_rel


def sanitize_class(name: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
    return sanitized.lower()


def collect_samples(source_root: Path, mapping_path: Path) -> List[Sample]:
    samples: List[Sample] = []
    for src_rel, dst_rel in read_mapping_file(mapping_path):
        if TOMATO_MARKER not in str(src_rel):
            continue
        class_name = sanitize_class(src_rel.parts[2].split(TOMATO_MARKER, 1)[1])
        src = source_root / src_rel
        filename = Path(dst_rel).name
        samples.append(Sample(source=src, cls=class_name, filename=filename))
    return samples


def split_train_val(samples: List[Sample], val_split: float, seed: int) -> Tuple[List[Sample], List[Sample]]:
    grouped: Dict[str, List[Sample]] = defaultdict(list)
    for sample in samples:
        grouped[sample.cls].append(sample)

    rng = random.Random(seed)
    train_split: List[Sample] = []
    val_split_samples: List[Sample] = []

    for cls, cls_samples in grouped.items():
        cls_samples = cls_samples.copy()
        rng.shuffle(cls_samples)
        val_size = int(len(cls_samples) * val_split)
        val_split_samples.extend(cls_samples[:val_size])
        train_split.extend(cls_samples[val_size:])

    return train_split, val_split_samples


def copy_sample(sample: Sample, destination_dir: Path, use_symlinks: bool) -> None:
    destination_dir.mkdir(parents=True, exist_ok=True)
    target_path = destination_dir / sample.filename
    if target_path.exists():
        return
    if use_symlinks:
        os.symlink(sample.source, target_path)
    else:
        shutil.copy2(sample.source, target_path)


def save_summary(target_root: Path, counts: Dict[str, Dict[str, int]]) -> None:
    summary_path = target_root / "dataset_summary.json"
    with summary_path.open("w", encoding="utf-8") as fp:
        json.dump(counts, fp, indent=2, sort_keys=True)


def main() -> None:
    args = parse_args()
    source_root = args.source_root
    target_root = args.target_root

    train_mapping = source_root / "data_distribution_for_SVM/train_mapping.txt"
    test_mapping = source_root / "data_distribution_for_SVM/test_mapping.txt"

    if not train_mapping.exists() or not test_mapping.exists():
        raise FileNotFoundError("Mapping files not found in data_distribution_for_SVM directory.")

    train_samples = collect_samples(source_root, train_mapping)
    test_samples = collect_samples(source_root, test_mapping)

    train_split, val_split_samples = split_train_val(train_samples, args.val_split, args.seed)

    counts: Dict[str, Dict[str, int]] = {"train": defaultdict(int), "val": defaultdict(int), "test": defaultdict(int)}  # type: ignore

    for sample in train_split:
        copy_sample(sample, target_root / "train" / sample.cls, args.use_symlinks)
        counts["train"][sample.cls] += 1

    for sample in val_split_samples:
        copy_sample(sample, target_root / "val" / sample.cls, args.use_symlinks)
        counts["val"][sample.cls] += 1

    for sample in test_samples:
        copy_sample(sample, target_root / "test" / sample.cls, args.use_symlinks)
        counts["test"][sample.cls] += 1

    counts_serializable = {split: dict(classes) for split, classes in counts.items()}
    save_summary(target_root, counts_serializable)

    print("Dataset prepared at:", target_root)
    print(json.dumps(counts_serializable, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

