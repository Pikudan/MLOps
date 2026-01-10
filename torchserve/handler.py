"""Custom TorchServe handler for tomato disease classification.

This handler performs:
1. Preprocessing: resize, normalize, convert to tensor
2. Inference: forward pass through the model
3. Postprocessing: convert logits to class probabilities
"""

import io
import json
import logging
import torch
from PIL import Image
from torchvision import transforms
from ts.torch_handler.base_handler import BaseHandler

logger = logging.getLogger(__name__)


class TomatoDiseaseHandler(BaseHandler):
    """Custom handler for tomato disease classification model."""

    def __init__(self):
        super().__init__()
        self.transform = None
        self.class_names = [
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
        self.image_size = 224

    def initialize(self, context):
        """Initialize model and transforms.
        
        Args:
            context: TorchServe context with model information
        """
        super().initialize(context)
        
        # Setup preprocessing transforms
        self.transform = transforms.Compose([
            transforms.Resize((self.image_size, self.image_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        logger.info("TomatoDiseaseHandler initialized successfully")
        logger.info("Number of classes: %d", len(self.class_names))

    def preprocess(self, data):
        """Preprocess input images.
        
        Args:
            data: List of input data (images as bytes)
            
        Returns:
            Batch tensor of preprocessed images
        """
        images = []
        
        for row in data:
            # Get image data
            if isinstance(row, dict):
                image_data = row.get("data") or row.get("body")
            else:
                image_data = row
            
            if isinstance(image_data, str):
                # Base64 encoded
                import base64
                image_data = base64.b64decode(image_data)
            
            # Open image
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            
            # Apply transforms
            tensor = self.transform(image)
            images.append(tensor)
        
        # Stack into batch
        batch = torch.stack(images)
        logger.debug("Preprocessed batch shape: %s", batch.shape)
        
        return batch

    def inference(self, data, *args, **kwargs):
        """Run model inference.
        
        Args:
            data: Preprocessed input tensor
            
        Returns:
            Model output logits
        """
        with torch.no_grad():
            data = data.to(self.device)
            outputs = self.model(data)
        return outputs

    def postprocess(self, inference_output):
        """Convert model output to predictions.
        
        Args:
            inference_output: Model output logits
            
        Returns:
            List of prediction dictionaries
        """
        # Apply softmax to get probabilities
        probabilities = torch.softmax(inference_output, dim=1)
        
        # Get top-k predictions
        top_k = min(3, len(self.class_names))
        top_probs, top_indices = torch.topk(probabilities, top_k, dim=1)
        
        results = []
        for probs, indices in zip(top_probs, top_indices):
            prediction = {
                "predicted_class": self.class_names[indices[0].item()],
                "confidence": round(probs[0].item(), 4),
                "top_predictions": [
                    {
                        "class": self.class_names[idx.item()],
                        "probability": round(prob.item(), 4)
                    }
                    for prob, idx in zip(probs, indices)
                ]
            }
            results.append(prediction)
        
        return results

    def handle(self, data, context):
        """Entry point for TorchServe.
        
        Args:
            data: Input data from request
            context: TorchServe context
            
        Returns:
            List of prediction results
        """
        try:
            if not self.initialized:
                self.initialize(context)
            
            if data is None:
                return [{"error": "No input data provided"}]
            
            preprocessed = self.preprocess(data)
            outputs = self.inference(preprocessed)
            results = self.postprocess(outputs)
            
            return results
            
        except Exception as e:
            logger.error("Error in handler: %s", str(e))
            return [{"error": str(e)}]

