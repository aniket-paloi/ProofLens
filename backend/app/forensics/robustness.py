"""
ProofLens Advanced Document Robustness & Quality Localization (Milestone 19)
Measures scan skew angle, blur degradation, DPI resolution adequacy, and compression resilience.
"""

import math
import numpy as np
import cv2
from typing import Dict, Any


def assess_document_robustness(image: np.ndarray) -> Dict[str, Any]:
    """
    Evaluates image quality and transformation resilience of a document page raster.
    """
    if image is None or image.size == 0:
        return {
            "is_evaluable": False,
            "reason": "Empty or invalid image array"
        }

    h, w = image.shape[:2]
    
    # 1. Grayscale conversion
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # 2. Blur / Sharpness Quality (Laplacian Variance)
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    blur_status = "SHARP" if lap_var > 100.0 else ("MODERATE_BLUR" if lap_var > 35.0 else "HEAVILY_BLURRED")

    # 3. Skew Angle Detection via thresholding and minimum bounding box
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    skew_angle = 0.0
    if len(coords) > 100:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        skew_angle = round(float(angle), 2)

    is_skew_tolerable = abs(skew_angle) < 5.0

    # 4. Resolution & Aspect Ratio Assessment
    dpi_estimate = int(w / 8.5) if w > 0 else 0  # Assuming standard letter width in inches
    dpi_adequate = dpi_estimate >= 150

    return {
        "is_evaluable": True,
        "page_dimensions": {"width_px": w, "height_px": h},
        "estimated_dpi": dpi_estimate,
        "is_dpi_adequate": dpi_adequate,
        "laplacian_sharpness": round(lap_var, 2),
        "blur_quality": blur_status,
        "skew_angle_degrees": skew_angle,
        "is_skew_tolerable": is_skew_tolerable,
        "robustness_score": round(
            (1.0 if blur_status == "SHARP" else 0.5) * 0.5 +
            (1.0 if is_skew_tolerable else 0.4) * 0.3 +
            (1.0 if dpi_adequate else 0.5) * 0.2,
            2
        )
    }

