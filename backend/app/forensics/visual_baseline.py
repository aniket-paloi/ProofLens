import os
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import cv2
import numpy as np
import pymupdf
from backend.app.core.config import settings

def extract_pixel_crop(
    gray_image: np.ndarray,
    bbox_norm: List[float]
) -> np.ndarray:
    """Extracts a pixel crop from a normalized bbox [ymin, xmin, ymax, xmax]."""
    h, w = gray_image.shape
    ymin, xmin, ymax, xmax = bbox_norm
    
    y0 = max(0, min(h - 1, int(ymin * h)))
    y1 = max(y0 + 1, min(h, int(ymax * h)))
    x0 = max(0, min(w - 1, int(xmin * w)))
    x1 = max(x0 + 1, min(w, int(xmax * w)))
    
    return gray_image[y0:y1, x0:x1]

def compute_laplacian_variance(crop: np.ndarray) -> float:
    """Computes Laplacian sharpness variance on an image patch."""
    if crop is None or crop.size < 4:
        return 0.0
    return float(cv2.Laplacian(crop, cv2.CV_64F).var())

def analyze_sharpness_variance(
    image_path: str,
    target_bbox_norm: List[float],
    context_bbox_norm: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Computes local sharpness ratio between target crop and surrounding context.
    Detects digitally spliced text patches with anomalous blur or sharpness profiles.
    """
    if not os.path.exists(image_path):
        return {"status": "FILE_NOT_FOUND", "ratio": 1.0, "is_anomaly": False}

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {"status": "LOAD_ERROR", "ratio": 1.0, "is_anomaly": False}

    target_crop = extract_pixel_crop(img, target_bbox_norm)
    target_var = compute_laplacian_variance(target_crop)

    # Use context bbox if provided, else horizontal band around the target
    if context_bbox_norm:
        context_crop = extract_pixel_crop(img, context_bbox_norm)
    else:
        # Context is horizontal band (+/- 2% vertical padding across 50% width)
        ymin, xmin, ymax, xmax = target_bbox_norm
        band_ymin = max(0.0, ymin - 0.02)
        band_ymax = min(1.0, ymax + 0.02)
        band_xmin = max(0.0, xmin - 0.25)
        band_xmax = min(1.0, xmax + 0.25)
        context_crop = extract_pixel_crop(img, [band_ymin, band_xmin, band_ymax, band_xmax])

    context_var = compute_laplacian_variance(context_crop)
    ratio = target_var / max(context_var, 1e-4)

    # Anomaly if target variance is severely mismatched with row context
    is_anomaly = (ratio > 3.0 or ratio < 0.30) and (abs(target_var - context_var) > 50.0)

    return {
        "status": "COMPLETED",
        "target_variance": round(target_var, 2),
        "context_variance": round(context_var, 2),
        "sharpness_ratio": round(ratio, 2),
        "is_anomaly": is_anomaly,
        "measured_value": round(ratio, 2),
        "threshold_upper": 3.0,
        "threshold_lower": 0.30
    }

def analyze_contrast_edge_discontinuity(
    image_path: str,
    target_bbox_norm: List[float]
) -> Dict[str, Any]:
    """
    Computes Sobel gradient magnitude along the boundary margin of a crop.
    Detects rectangular paste step borders or white-out halos.
    """
    if not os.path.exists(image_path):
        return {"status": "FILE_NOT_FOUND", "is_anomaly": False, "boundary_gradient": 0.0}

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {"status": "LOAD_ERROR", "is_anomaly": False, "boundary_gradient": 0.0}

    crop = extract_pixel_crop(img, target_bbox_norm)
    if crop.shape[0] < 6 or crop.shape[1] < 6:
        return {"status": "CROP_TOO_SMALL", "is_anomaly": False, "boundary_gradient": 0.0}

    # Sobel gradient
    sobelx = cv2.Sobel(crop, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(crop, cv2.CV_64F, 0, 1, ksize=3)
    grad_mag = np.sqrt(sobelx**2 + sobely**2)

    # Margin border pixels (1-2px border)
    border_pixels = np.concatenate([
        grad_mag[0:2, :].flatten(),
        grad_mag[-2:, :].flatten(),
        grad_mag[:, 0:2].flatten(),
        grad_mag[:, -2:].flatten()
    ])

    border_mean = float(np.mean(border_pixels))
    interior_mean = float(np.mean(grad_mag[2:-2, 2:-2])) if grad_mag.shape[0] > 4 and grad_mag.shape[1] > 4 else 0.0
    
    # Anomaly when outer border has abnormal sharp boundary edge compared to interior
    border_ratio = border_mean / max(interior_mean, 1e-4)
    is_anomaly = (border_ratio > 4.5 and border_mean > 120.0)

    return {
        "status": "COMPLETED",
        "border_gradient_mean": round(border_mean, 2),
        "interior_gradient_mean": round(interior_mean, 2),
        "border_ratio": round(border_ratio, 2),
        "is_anomaly": is_anomaly,
        "measured_value": round(border_ratio, 2),
        "threshold": 4.5
    }

def analyze_native_font_consistency(
    pdf_path: str,
    page_number: int
) -> Dict[str, Any]:
    """
    Inspects PyMuPDF span font names, sizes, and weights on the page.
    Flags font family outliers among numeric fields.
    """
    if not os.path.exists(pdf_path):
        return {"status": "FILE_NOT_FOUND", "is_consistent": True, "anomalies": []}

    doc = pymupdf.open(pdf_path)
    if page_number < 1 or page_number > len(doc):
        doc.close()
        return {"status": "PAGE_OUT_OF_RANGE", "is_consistent": True, "anomalies": []}

    page = doc[page_number - 1]
    width = float(page.rect.width)
    height = float(page.rect.height)
    page_dict = page.get_text("dict")

    numeric_spans = []
    font_family_counts: Dict[str, int] = {}

    for block in page_dict.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if not text:
                    continue
                font_name = span.get("font", "Unknown")
                font_family_counts[font_name] = font_family_counts.get(font_name, 0) + 1

                # If span contains digits (currency/amounts)
                if any(c.isdigit() for c in text):
                    bbox = span.get("bbox", [0, 0, 0, 0])
                    norm_bbox = [
                        round(bbox[1] / height, 4),
                        round(bbox[0] / width, 4),
                        round(bbox[3] / height, 4),
                        round(bbox[2] / width, 4),
                    ]
                    numeric_spans.append({
                        "text": text,
                        "font_name": font_name,
                        "font_size": span.get("size", 10.0),
                        "bbox_normalized": norm_bbox
                    })

    doc.close()

    if not font_family_counts:
        return {"status": "NO_TEXT", "is_consistent": True, "anomalies": []}

    # Predominant font family on the page
    dominant_font = max(font_family_counts, key=font_family_counts.get)
    anomalies = []

    for span in numeric_spans:
        # If numeric span font is completely different family and infrequent (<10% frequency)
        if span["font_name"] != dominant_font and font_family_counts.get(span["font_name"], 0) <= 2:
            anomalies.append({
                "text": span["text"],
                "font_name": span["font_name"],
                "expected_font": dominant_font,
                "bbox_normalized": span["bbox_normalized"]
            })

    return {
        "status": "COMPLETED",
        "dominant_font": dominant_font,
        "is_consistent": len(anomalies) == 0,
        "anomalies": anomalies
    }

def save_crop_derivative(
    image_path: str,
    bbox_norm: List[float],
    crop_prefix: str = "crop"
) -> Optional[str]:
    """
    Saves a high-resolution PNG crop derivative to storage/derivatives/crops/.
    Returns relative or absolute file path.
    """
    if not os.path.exists(image_path):
        return None

    img = cv2.imread(image_path)
    if img is None:
        return None

    h, w, _ = img.shape
    ymin, xmin, ymax, xmax = bbox_norm
    y0 = max(0, min(h - 1, int(ymin * h)))
    y1 = max(y0 + 1, min(h, int(ymax * h)))
    x0 = max(0, min(w - 1, int(xmin * w)))
    x1 = max(x0 + 1, min(w, int(xmax * w)))

    crop = img[y0:y1, x0:x1]
    crop_id = f"{crop_prefix}_{uuid.uuid4().hex[:12]}.png"
    crop_dir = settings.DERIVATIVES_DIR / "crops"
    crop_dir.mkdir(parents=True, exist_ok=True)
    full_crop_path = crop_dir / crop_id
    
    cv2.imwrite(str(full_crop_path), crop)
    return str(full_crop_path)

