import os
from pathlib import Path
from typing import Dict, Any, Optional
import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.models import mobilenet_v3_small

class RegionClassifierAdapter:
    """
    Adapter for loading and running the trained MobileNetV3 Small region classifier.
    """
    def __init__(self, checkpoint_path: Optional[str] = None):
        self.device = torch.device("cpu")
        if checkpoint_path is None:
            checkpoint_path = os.path.join("ml", "checkpoints", "mobilenet_v3_small_region.pt")
        
        self.checkpoint_path = checkpoint_path
        self.model = self._load_model()
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def _load_model(self) -> Optional[nn.Module]:
        if not os.path.exists(self.checkpoint_path):
            return None

        try:
            model = mobilenet_v3_small(weights=None)
            num_ftrs = model.classifier[3].in_features
            model.classifier[3] = nn.Linear(num_ftrs, 1)

            checkpoint = torch.load(self.checkpoint_path, map_location=self.device, weights_only=False)
            model.load_state_dict(checkpoint["model_state_dict"])
            model.eval()
            return model
        except Exception as e:
            return None

    def predict_crop(self, crop_image_path: str) -> Dict[str, Any]:
        """
        Runs inference on an image crop and returns manipulation probability.
        """
        if self.model is None or not os.path.exists(crop_image_path):
            return {
                "status": "UNAVAILABLE",
                "manipulation_probability": 0.0,
                "is_anomaly": False,
                "threshold": 0.50
            }

        try:
            img = cv2.imread(crop_image_path)
            if img is None:
                return {
                    "status": "LOAD_ERROR",
                    "manipulation_probability": 0.0,
                    "is_anomaly": False,
                    "threshold": 0.50
                }

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            tensor = self.transform(img_rgb).unsqueeze(0).to(self.device)

            with torch.no_grad():
                logit = self.model(tensor)
                prob = float(torch.sigmoid(logit).item())

            return {
                "status": "COMPLETED",
                "manipulation_probability": round(prob, 4),
                "is_anomaly": prob >= 0.50,
                "threshold": 0.50
            }
        except Exception as e:
            return {
                "status": "INFERENCE_ERROR",
                "error": str(e),
                "manipulation_probability": 0.0,
                "is_anomaly": False,
                "threshold": 0.50
            }

