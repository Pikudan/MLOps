import pytest
import torch

from src.utils import logits_to_probabilities, probabilities_to_predictions


def test_logits_to_probabilities_and_predictions() -> None:
    logits = torch.tensor([[2.0, 1.0, 0.0]])
    probs = logits_to_probabilities(logits)

    assert torch.allclose(probs.sum(dim=-1), torch.tensor([1.0]))
    assert torch.argmax(probs, dim=-1).item() == 0

    class_names = ["tomato", "cabbage", "background"]
    preds = probabilities_to_predictions(probs, class_names)
    assert preds[0]["label"] == "tomato"
    assert preds[0]["score"] == pytest.approx(0.665, rel=1e-2)

