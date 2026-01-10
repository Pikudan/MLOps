"""Export trained model to TorchScript format for TorchServe.

Usage:
    python torchserve/export_model.py --model-dir training/models/tomato --output torchserve/model.pt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from training.classification.src.model import SimpleCNN


def export_model(model_dir: Path, output_path: Path, image_size: int = 224):
    """Export model to TorchScript format.
    
    Args:
        model_dir: Path to trained model directory
        output_path: Path to save TorchScript model
        image_size: Input image size
    """
    print(f"Loading model from: {model_dir}")
    
    # Load trained model
    model = SimpleCNN.from_pretrained(model_dir, map_location="cpu")
    model.eval()
    
    print(f"Model loaded. Num classes: {model.num_classes}")
    
    # Create example input for tracing
    example_input = torch.randn(1, 3, image_size, image_size)
    
    # Trace the model
    print("Tracing model...")
    traced_model = torch.jit.trace(model, example_input)
    
    # Verify traced model
    with torch.no_grad():
        original_output = model(example_input)
        traced_output = traced_model(example_input)
        
        if not torch.allclose(original_output, traced_output, atol=1e-6):
            print("WARNING: Traced model output differs from original!")
        else:
            print("Traced model verified successfully")
    
    # Save traced model
    output_path.parent.mkdir(parents=True, exist_ok=True)
    traced_model.save(str(output_path))
    print(f"TorchScript model saved to: {output_path}")
    
    # Print model info
    print(f"\nModel info:")
    print(f"  - Input shape: (batch, 3, {image_size}, {image_size})")
    print(f"  - Output shape: (batch, {model.num_classes})")
    print(f"  - File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")


def main():
    parser = argparse.ArgumentParser(description="Export model to TorchScript")
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=Path("training/models/tomato"),
        help="Path to trained model directory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("torchserve/model.pt"),
        help="Output path for TorchScript model"
    )
    parser.add_argument(
        "--image-size",
        type=int,
        default=224,
        help="Input image size"
    )
    
    args = parser.parse_args()
    export_model(args.model_dir, args.output, args.image_size)


if __name__ == "__main__":
    main()

