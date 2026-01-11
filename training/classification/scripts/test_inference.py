"""Inference script for test dataset using the best model.

Usage:
    python training/classification/scripts/test_inference.py \
        --model-dir training/models/tomato_large \
        --test-dir training/classification/datasets/tomato/test \
        --output outputs/test_predictions.csv
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import List, Tuple

import torch
import pandas as pd
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

import sys
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from training.classification.src.model import SimpleCNN

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
LOGGER = logging.getLogger(__name__)


def load_model(model_dir: Path, device: torch.device) -> SimpleCNN:
    """Load trained model from directory."""
    LOGGER.info("Loading model from: %s", model_dir)
    model = SimpleCNN.from_pretrained(model_dir, map_location=str(device))
    model.to(device)
    model.eval()
    LOGGER.info("Model loaded successfully")
    return model


def create_test_loader(test_dir: Path, image_size: int = 224, batch_size: int = 32) -> Tuple[DataLoader, List[str]]:
    """Create test data loader."""
    transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    dataset = datasets.ImageFolder(root=str(test_dir), transform=transform)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    
    return loader, dataset.classes


@torch.no_grad()
def run_inference(
    model: SimpleCNN,
    loader: DataLoader,
    device: torch.device,
    class_names: List[str],
    dataset: datasets.ImageFolder
) -> pd.DataFrame:
    """Run inference on test dataset and return predictions with file paths."""
    results = []
    
    LOGGER.info("Running inference on %d samples...", len(dataset))
    
    for batch_idx, (inputs, labels) in enumerate(loader):
        inputs = inputs.to(device)
        outputs = model(inputs)
        probs = torch.softmax(outputs, dim=1)
        confidences, predictions = torch.max(probs, dim=1)
        
        # Get file paths for this batch
        start_idx = batch_idx * loader.batch_size
        for i, (pred_idx, conf, true_label) in enumerate(zip(predictions, confidences, labels)):
            sample_idx = start_idx + i
            if sample_idx < len(dataset):
                file_path = dataset.samples[sample_idx][0]
                file_name = Path(file_path).name
                true_class = class_names[true_label.item()]
                pred_class = class_names[pred_idx.item()]
                
                results.append({
                    "file_path": str(file_path),
                    "filename": file_name,
                    "true_class": true_class,
                    "predicted_class": pred_class,
                    "confidence": round(conf.item(), 4),
                    "class_index": pred_idx.item(),
                    "correct": true_class == pred_class
                })
    
    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(description="Run inference on test dataset")
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=Path("training/models/tomato_large"),
        help="Path to trained model directory (best model: tomato_large)"
    )
    parser.add_argument(
        "--test-dir",
        type=Path,
        default=Path("training/classification/datasets/tomato/test"),
        help="Path to test dataset directory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/test_predictions.csv"),
        help="Output CSV file with predictions"
    )
    parser.add_argument(
        "--image-size",
        type=int,
        default=224,
        help="Image size for inference"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for inference"
    )
    args = parser.parse_args()
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    LOGGER.info("Using device: %s", device)
    
    # Load model
    model = load_model(args.model_dir, device)
    
    # Create test loader
    LOGGER.info("Loading test data from: %s", args.test_dir)
    transform = transforms.Compose([
        transforms.Resize((args.image_size, args.image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    dataset = datasets.ImageFolder(root=str(args.test_dir), transform=transform)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)
    class_names = dataset.classes
    
    LOGGER.info("Found %d classes: %s", len(class_names), class_names)
    LOGGER.info("Total test samples: %d", len(dataset))
    
    # Run inference
    predictions_df = run_inference(model, loader, device, class_names, dataset)
    
    # Calculate accuracy
    accuracy = predictions_df["correct"].mean()
    LOGGER.info("=" * 60)
    LOGGER.info("Test Accuracy: %.4f (%.2f%%)", accuracy, accuracy * 100)
    LOGGER.info("Correct predictions: %d / %d", predictions_df["correct"].sum(), len(predictions_df))
    LOGGER.info("=" * 60)
    
    # Save predictions
    args.output.parent.mkdir(parents=True, exist_ok=True)
    predictions_df.to_csv(args.output, index=False)
    LOGGER.info("Predictions saved to: %s", args.output)
    
    # Save summary
    summary_path = args.output.parent / f"{args.output.stem}_summary.txt"
    with open(summary_path, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("Test Inference Summary\n")
        f.write("=" * 60 + "\n")
        f.write(f"Model: {args.model_dir}\n")
        f.write(f"Test Dataset: {args.test_dir}\n")
        f.write(f"Total Samples: {len(predictions_df)}\n")
        f.write(f"Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)\n")
        f.write(f"Correct: {predictions_df['correct'].sum()} / {len(predictions_df)}\n")
        f.write("=" * 60 + "\n")
        f.write("\nPer-class accuracy:\n")
        for class_name in class_names:
            class_df = predictions_df[predictions_df["true_class"] == class_name]
            if len(class_df) > 0:
                class_acc = class_df["correct"].mean()
                f.write(f"  {class_name}: {class_acc:.4f} ({len(class_df)} samples)\n")
    
    LOGGER.info("Summary saved to: %s", summary_path)


if __name__ == "__main__":
    main()

