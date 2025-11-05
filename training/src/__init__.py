"""Training package exports."""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

_current_module = inspect.getmodule(inspect.currentframe())
if _current_module is not None:
    sys.modules.setdefault(__name__, _current_module)

_PACKAGE_DIR = Path(__file__).resolve().parent

if __spec__ is not None and __spec__.submodule_search_locations is None:  # type: ignore[name-defined]
    __spec__.submodule_search_locations = [str(_PACKAGE_DIR)]  # type: ignore[attr-defined]

if "__path__" not in globals():
    __path__ = [str(_PACKAGE_DIR)]  # type: ignore[assignment]

if not __package__:
    __package__ = __name__

from .config import ConfigError, TrainingConfig, load_config
from .data import create_dataloaders, describe_dataset
from .model import SimpleCNN, build_model
from .trainer import Trainer
from .utils import logits_to_probabilities, probabilities_to_predictions, set_seed, setup_logging

__all__ = [
    "TrainingConfig",
    "load_config",
    "ConfigError",
    "create_dataloaders",
    "describe_dataset",
    "SimpleCNN",
    "build_model",
    "Trainer",
    "logits_to_probabilities",
    "probabilities_to_predictions",
    "set_seed",
    "setup_logging",
]

