"""Training package exports."""

from .config import ConfigError, TrainingConfig, load_config
from .data import (
    build_dataset,
    build_transforms,
    create_dataloaders,
    describe_dataset,
    load_imagefolder_dataset,
)
from .model import SimpleCNN, build_model
from .trainer import Trainer
from .utils import logits_to_probabilities, probabilities_to_predictions, set_seed, setup_logging
from .validation import (
    BatchValidationError,
    ensure_directory_structure,
    validate_batch,
    validate_class_names,
    validate_image_tensor,
    validate_label_tensor,
    validate_probability_tensor,
)

__all__ = [
    "ConfigError",
    "TrainingConfig",
    "load_config",
    "build_dataset",
    "build_transforms",
    "create_dataloaders",
    "describe_dataset",
    "load_imagefolder_dataset",
    "SimpleCNN",
    "build_model",
    "Trainer",
    "logits_to_probabilities",
    "probabilities_to_predictions",
    "set_seed",
    "setup_logging",
    "ensure_directory_structure",
    "validate_batch",
    "validate_class_names",
    "validate_image_tensor",
    "validate_label_tensor",
    "validate_probability_tensor",
    "BatchValidationError",
]

