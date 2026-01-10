"""Model evaluation script for DVC pipeline."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    classification_report,
    confusion_matrix
)
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from model import SimpleCNN

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
LOGGER = logging.getLogger(__name__)


def load_model(model_dir: Path, device: torch.device) -> SimpleCNN:
    """Load trained model from directory."""
    model = SimpleCNN.from_pretrained(model_dir, map_location=str(device))
    model.to(device)
    model.eval()
    return model


def create_test_loader(test_dir: Path, image_size: int = 224, batch_size: int = 32) -> DataLoader:
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
def evaluate_model(model: SimpleCNN, loader: DataLoader, device: torch.device) -> tuple:
    """Evaluate model on test set."""
    all_preds = []
    all_labels = []
    all_probs = []
    
    for inputs, labels in loader:
        inputs = inputs.to(device)
        outputs = model(inputs)
        probs = torch.softmax(outputs, dim=1)
        _, preds = torch.max(outputs, dim=1)
        
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.numpy())
        all_probs.extend(probs.cpu().numpy())
    
    return np.array(all_preds), np.array(all_labels), np.array(all_probs)


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, class_names: list) -> Dict[str, Any]:
    """Compute evaluation metrics."""
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "precision_weighted": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall_weighted": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1_weighted": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
    }
    
    # Per-class metrics
    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0)
    metrics["per_class"] = {name: report[name] for name in class_names if name in report}
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    metrics["confusion_matrix"] = cm.tolist()
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Evaluate trained model")
    parser.add_argument("--model-dir", type=Path, required=True, help="Path to trained model directory")
    parser.add_argument("--test-dir", type=Path, required=True, help="Path to test dataset directory")
    parser.add_argument("--output", type=Path, default=Path("metrics.json"), help="Output metrics file")
    parser.add_argument("--image-size", type=int, default=224, help="Image size for inference")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for inference")
    args = parser.parse_args()
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    LOGGER.info("Using device: %s", device)
    
    # Load model
    LOGGER.info("Loading model from: %s", args.model_dir)
    model = load_model(args.model_dir, device)
    
    # Create test loader
    LOGGER.info("Loading test data from: %s", args.test_dir)
    loader, class_names = create_test_loader(args.test_dir, args.image_size, args.batch_size)
    LOGGER.info("Found %d classes: %s", len(class_names), class_names)
    
    # Evaluate
    LOGGER.info("Evaluating model...")
    y_pred, y_true, y_probs = evaluate_model(model, loader, device)
    
    # Compute metrics
    metrics = compute_metrics(y_true, y_pred, class_names)
    metrics["num_samples"] = len(y_true)
    metrics["class_names"] = class_names
    
    LOGGER.info("Accuracy: %.4f", metrics["accuracy"])
    LOGGER.info("F1 (macro): %.4f", metrics["f1_macro"])
    LOGGER.info("Precision (macro): %.4f", metrics["precision_macro"])
    LOGGER.info("Recall (macro): %.4f", metrics["recall_macro"])
    
    # Save metrics
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(metrics, f, indent=2)
    
    LOGGER.info("Metrics saved to: %s", args.output)


if __name__ == "__main__":
    main()

