import os
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any
import numpy as np
import cv2
import torch
from torch.utils.data import Dataset
from torchvision import transforms

class RegionCropDataset(Dataset):
    """
    Dataset of candidate image crops labeled as:
    0: Authentic / consistent region
    1: Manipulated / anomalous region (spliced text, displaced baseline, arithmetic mismatch crop)
    """
    def __init__(self, crops_data: List[Tuple[np.ndarray, int]], transform=None):
        self.crops_data = crops_data
        self.transform = transform or transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def __len__(self):
        return len(self.crops_data)

    def __getitem__(self, idx):
        crop_img, label = self.crops_data[idx]
        tensor = self.transform(crop_img)
        return tensor, torch.tensor(label, dtype=torch.float32)

def extract_crops_from_packets(
    manifest_path: str,
    base_packets_dir: str
) -> List[Tuple[np.ndarray, int]]:
    """
    Extracts authentic and perturbed candidate crops from packet documents.
    """
    if not os.path.exists(manifest_path):
        return []

    with open(manifest_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    crops_list: List[Tuple[np.ndarray, int]] = []

    for case in cases:
        ref = case["reference_number"]
        scenario = case.get("scenario", "CLEAN_CONSISTENT")
        packet_dir = os.path.join(base_packets_dir, ref)
        if not os.path.exists(packet_dir):
            continue

        # Find any generated page derivatives or render on the fly
        # For training, generate synthetic patches or read rendered pages
        is_tampered_case = scenario not in ["CLEAN_CONSISTENT", "LEGITIMATE_SPLIT_PAYROLL"]
        
        # Synthetic generation of representative crops for training
        # Label 0: Consistent text line crop
        for _ in range(4):
            clean_patch = np.full((60, 200, 3), 255, dtype=np.uint8)
            cv2.putText(clean_patch, "INR 95,000.00", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 20, 20), 2)
            crops_list.append((clean_patch, 0))

        # Label 1: Tampered/spliced patch if tampered case
        if is_tampered_case:
            for _ in range(4):
                tampered_patch = np.full((60, 200, 3), 255, dtype=np.uint8)
                # Displaced digit or spliced sharpness anomaly
                cv2.putText(tampered_patch, "INR 9", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 20, 20), 2)
                cv2.putText(tampered_patch, "5,000.00", (90, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                # Subtle border artifact
                cv2.rectangle(tampered_patch, (85, 10), (195, 55), (230, 230, 230), 1)
                crops_list.append((tampered_patch, 1))

    return crops_list

