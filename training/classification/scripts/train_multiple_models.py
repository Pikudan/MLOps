"""Train multiple models with different hyperparameters for multiclass classification.

Usage:
    python training/classification/scripts/train_multiple_models.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Model configurations to train (config files)
MODEL_CONFIGS = [
    {
        "name": "simple_cnn_small",
        "config": "training/classification/configs/multiclass/model_small.yaml",
        "description": "Small model: hidden_dim=32, dropout=0.2, lr=0.001"
    },
    {
        "name": "simple_cnn_medium",
        "config": "training/classification/configs/multiclass/model_medium.yaml",
        "description": "Medium model: hidden_dim=64, dropout=0.3, lr=0.0005"
    },
    {
        "name": "simple_cnn_large",
        "config": "training/classification/configs/multiclass/model_large.yaml",
        "description": "Large model: hidden_dim=128, dropout=0.4, lr=0.0003"
    },
    {
        "name": "simple_cnn_deep",
        "config": "training/classification/configs/multiclass/model_deep.yaml",
        "description": "Deep model: hidden_dim=64, dropout=0.5, lr=0.0001, epochs=15"
    },
]


def train_model(config: dict, project_root: Path) -> bool:
    """Train a single model with given configuration."""
    print(f"\n{'='*60}")
    print(f"Training model: {config['name']}")
    print(f"Description: {config['description']}")
    print(f"{'='*60}")
    
    config_path = project_root / config["config"]
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return False
    
    cmd = [
        sys.executable,
        "-m", "training.classification.train",
        str(config_path),
        "--experiment-name", "Multiclass-Model-Comparison",
        "--run-name", config["name"],
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode != 0:
        print(f"❌ Training failed for {config['name']}")
        return False
    else:
        print(f"✅ Training completed for {config['name']}")
        return True


def main():
    project_root = Path(__file__).parent.parent.parent.parent
    
    print(f"{'='*60}")
    print("Training Multiple Models for Multiclass Classification")
    print(f"{'='*60}")
    print(f"\nWill train {len(MODEL_CONFIGS)} models:")
    for i, config in enumerate(MODEL_CONFIGS, 1):
        print(f"  {i}. {config['name']}: {config['description']}")
    
    print(f"\nAll models will be logged to MLflow experiment: 'Multiclass-Model-Comparison'")
    print(f"Project root: {project_root}\n")
    
    results = []
    for config in MODEL_CONFIGS:
        success = train_model(config, project_root)
        results.append((config['name'], success))
    
    print(f"\n{'='*60}")
    print("Training Summary")
    print(f"{'='*60}")
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print(f"\n{'='*60}")
    print("View results in MLflow:")
    print("  mlflow ui --port 5000")
    print("  http://localhost:5000")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

