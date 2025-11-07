# pyright: reportMissingImports=false

import torch

import pytest

from training.classification.src import (
    logits_to_probabilities,
    probabilities_to_predictions,
    validate_probability_tensor,
)


def test_logits_to_probabilities_and_predictions() -> None:
    logits = torch.tensor([[2.0, 1.0, 0.0]])
    probs = logits_to_probabilities(logits)

    assert torch.allclose(probs.sum(dim=-1), torch.tensor([1.0]))
    assert torch.argmax(probs, dim=-1).item() == 0

    class_names = ["tomato", "cabbage", "background"]
    preds = probabilities_to_predictions(probs, class_names)
    assert preds[0]["label"] == "tomato"
    assert preds[0]["score"] == pytest.approx(0.665, rel=1e-2)


def test_probabilities_validation() -> None:
    probs = torch.tensor([[0.4, 0.4, 0.2]])
    validate_probability_tensor(probs)

    bad_probs = torch.tensor([[0.4, 0.4, 0.3]])
    with pytest.raises(ValueError):
        validate_probability_tensor(bad_probs)

    with pytest.raises(ValueError):
        probabilities_to_predictions(bad_probs)

    with pytest.raises(ValueError):
        probabilities_to_predictions(probs, class_names=["a", "b"])  # mismatched names

