"""Offline inference script for Docker container.

Usage:
    python -m src.predict --input_path /data/input --output_path /data/preds.csv

Input: Directory with images or single image file
Output: CSV file with predictions (filename, predicted_class, confidence)
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Tuple

import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image
import pandas as pd

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from training.classification.src.model import SimpleCNN
from training.classification.src.config import ModelConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

# Default class names for tomato disease classification
DEFAULT_CLASS_NAMES = [
    "bacterial_spot",
    "early_blight",
    "healthy",
    "late_blight",
    "leaf_mold",
    "septoria_leaf_spot",
    "spider_mites_two_spotted_spider_mite",
    "target_spot",
    "tomato_mosaic_virus",
    "tomato_yellow_leaf_curl_virus"
]


class ImageDataset(Dataset):
    """Simple dataset for inference on image files."""
    
    def __init__(self, image_paths: List[Path], transform: transforms.Compose):
        self.image_paths = image_paths
        self.transform = transform
    
    def __len__(self) -> int:
        return len(self.image_paths)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, str]:
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert("RGB")
        image_tensor = self.transform(image)
        return image_tensor, image_path.name


def get_image_paths(input_path: Path) -> List[Path]:
    """Get list of image files from input path."""
    supported_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".JPG", ".JPEG", ".PNG"}
    
    if input_path.is_file():
        if input_path.suffix in supported_extensions:
            return [input_path]
        else:
            raise ValueError(f"Unsupported file format: {input_path.suffix}")
    
    if input_path.is_dir():
        image_paths = []
        for ext in supported_extensions:
            image_paths.extend(input_path.glob(f"*{ext}"))
            image_paths.extend(input_path.glob(f"**/*{ext}"))  # Recursive search
        return sorted(set(image_paths))
    
    raise FileNotFoundError(f"Input path not found: {input_path}")


def load_model(model_dir: Path, device: torch.device) -> SimpleCNN:
    """Load trained model from directory."""
    LOGGER.info("Loading model from: %s", model_dir)
    
    if not model_dir.exists():
        raise FileNotFoundError(f"Model directory not found: {model_dir}")
    
    model = SimpleCNN.from_pretrained(model_dir, map_location=str(device))
    model.to(device)
    model.eval()
    
    LOGGER.info("Model loaded successfully. Num classes: %d", model.num_classes)
    return model


def create_transform(image_size: int = 224) -> transforms.Compose:
    """Create preprocessing transform for inference."""
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])


@torch.no_grad()
def predict(
    model: SimpleCNN,
    loader: DataLoader,
    device: torch.device,
    class_names: List[str]
) -> pd.DataFrame:
    """Run inference on images and return predictions."""
    
    results = []
    
    for batch_images, batch_filenames in loader:
        batch_images = batch_images.to(device)
        outputs = model(batch_images)
        probs = torch.softmax(outputs, dim=1)
        confidences, predictions = torch.max(probs, dim=1)
        
        for filename, pred_idx, conf in zip(batch_filenames, predictions, confidences):
            pred_class = class_names[pred_idx.item()] if pred_idx.item() < len(class_names) else f"class_{pred_idx.item()}"
            results.append({
                "filename": filename,
                "predicted_class": pred_class,
                "confidence": round(conf.item(), 4),
                "class_index": pred_idx.item()
            })
    
    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(
        description="Offline inference for tomato disease classification"
    )
    parser.add_argument(
        "--input_path", 
        type=Path, 
        required=True,
        help="Path to input image or directory with images"
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        required=True,
        help="Path to output CSV file with predictions"
    )
    parser.add_argument(
        "--model_dir",
        type=Path,
        default=Path("training/models/tomato"),
        help="Path to trained model directory"
    )
    parser.add_argument(
        "--image_size",
        type=int,
        default=224,
        help="Image size for preprocessing"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=32,
        help="Batch size for inference"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda"],
        help="Device to run inference on"
    )
    
    args = parser.parse_args()
    
    # Determine device
    if args.device == "cuda" and not torch.cuda.is_available():
        LOGGER.warning("CUDA not available, falling back to CPU")
        device = torch.device("cpu")
    else:
        device = torch.device(args.device)
    LOGGER.info("Using device: %s", device)
    
    # Get image paths
    image_paths = get_image_paths(args.input_path)
    if not image_paths:
        LOGGER.error("No images found in: %s", args.input_path)
        sys.exit(1)
    LOGGER.info("Found %d images to process", len(image_paths))
    
    # Load model
    model = load_model(args.model_dir, device)
    
    # Create dataset and dataloader
    transform = create_transform(args.image_size)
    dataset = ImageDataset(image_paths, transform)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)
    
    # Run inference
    LOGGER.info("Running inference...")
    predictions_df = predict(model, loader, device, DEFAULT_CLASS_NAMES)
    
    # Save results
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    predictions_df.to_csv(args.output_path, index=False)
    LOGGER.info("Predictions saved to: %s", args.output_path)
    LOGGER.info("Total predictions: %d", len(predictions_df))
    
    # Print summary
    print("\n=== Prediction Summary ===")
    print(predictions_df.groupby("predicted_class").size().sort_values(ascending=False))


if __name__ == "__main__":
    main()

