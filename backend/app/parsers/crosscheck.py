import pymupdf
from typing import List, Dict, Any, Optional

PROMPT_INJECTION_KEYWORDS = [
    "system prompt", "override", "disregard", "ignore previous instructions",
    "approve loan", "jailbreak", "bypass", "assistant instructions", "developer mode",
    "ignore all previous"
]

FINANCIAL_LABEL_TOKENS = [
    "net", "payable", "gross", "basic", "inr", "total", "salary", "earnings", "deductions", "balance"
]

def crosscheck_page_text_layers(pdf_path: str, page_number: int) -> Dict[str, Any]:
    """
    Analyzes page vector text spans, colors, baselines, and boundaries.
    Detects:
    1. Invisible/hidden text (white-on-white, near-white, or off-canvas text).
    2. Prompt injection attempts embedded in hidden text layers.
    3. Font baseline displacement anomalies (vertical shifts between adjacent labels and numeric values).
    """
    doc = pymupdf.open(pdf_path)
    if page_number < 1 or page_number > len(doc):
        doc.close()
        raise ValueError(f"Page number {page_number} out of range")

    page = doc[page_number - 1]
    width = float(page.rect.width)
    height = float(page.rect.height)

    # Extract detailed span information using PyMuPDF dict mode
    page_dict = page.get_text("dict")
    
    invisible_spans = []
    baseline_anomalies = []
    injected_prompts = []
    all_spans = []
    total_spans = 0

    for block in page_dict.get("blocks", []):
        if block.get("type") != 0:  # 0 = text block, 1 = image block
            continue

        for line in block.get("lines", []):
            spans = line.get("spans", [])
            for span in spans:
                total_spans += 1
                text = span.get("text", "").strip()
                if not text:
                    continue

                bbox = span.get("bbox", [0, 0, 0, 0])  # (x0, y0, x1, y1)
                origin = span.get("origin", [bbox[0], bbox[3]])  # (x, y) baseline origin
                x0, y0, x1, y1 = bbox
                font_size = span.get("size", 10.0)
                font_color = span.get("color", 0)  # RGB integer

                # Decode RGB integer to (r, g, b) in [0..255]
                r = (font_color >> 16) & 255
                g = (font_color >> 8) & 255
                b = font_color & 255

                # 1. Detect White-on-White or near-white invisible text
                is_white = (r >= 245 and g >= 245 and b >= 245)
                is_zero_size = font_size < 1.5
                is_off_canvas = (x1 < 0 or x0 > width or y1 < 0 or y0 > height)

                normalized_bbox = [
                    round(max(0.0, min(1.0, y0 / height)), 4),
                    round(max(0.0, min(1.0, x0 / width)), 4),
                    round(max(0.0, min(1.0, y1 / height)), 4),
                    round(max(0.0, min(1.0, x1 / width)), 4),
                ]

                span_record = {
                    "text": text,
                    "bbox": bbox,
                    "origin": origin,
                    "font_size": font_size,
                    "color_rgb": [r, g, b],
                    "normalized_bbox": normalized_bbox
                }
                all_spans.append(span_record)

                if is_white or is_zero_size or is_off_canvas:
                    inv_meta = {
                        "text": text,
                        "reason": "white_on_white" if is_white else ("zero_size" if is_zero_size else "off_canvas"),
                        "font_size": font_size,
                        "color_rgb": [r, g, b],
                        "bbox_original": [round(coord, 2) for coord in bbox],
                        "bbox_normalized": normalized_bbox
                    }
                    invisible_spans.append(inv_meta)

                    # Check for prompt injection keywords
                    text_lower = text.lower()
                    if any(kw in text_lower for kw in PROMPT_INJECTION_KEYWORDS):
                        matched_kw = next(kw for kw in PROMPT_INJECTION_KEYWORDS if kw in text_lower)
                        injected_prompts.append({
                            "matched_keyword": matched_kw,
                            "full_text": text,
                            "bbox_normalized": normalized_bbox
                        })

    # 2. Check for Font Baseline Anomalies across horizontally adjacent spans
    # Sort spans by vertical baseline origin y, then horizontal origin x
    all_spans.sort(key=lambda s: (round(s["origin"][1], 1), round(s["origin"][0], 1)))
    
    seen_pairs = set()
    for i in range(len(all_spans)):
        for j in range(i + 1, len(all_spans)):
            s1 = all_spans[i]
            s2 = all_spans[j]

            # Spans on approximately the same horizontal row (within 10px vertical window)
            y_delta = abs(s1["origin"][1] - s2["origin"][1])
            if y_delta <= 10.0:
                # Horizontal proximity: s2 is to the right of s1 within reasonable column distance
                x_dist = s2["bbox"][0] - s1["bbox"][2]
                if 0.0 <= x_dist <= 150.0:
                    t1_lower = s1["text"].lower()
                    t2 = s2["text"]
                    
                    # Check if s1 is a financial label/token and s2 is a numeric value
                    is_label_num_pair = (
                        any(tok in t1_lower for tok in FINANCIAL_LABEL_TOKENS)
                        and any(c.isdigit() for c in t2)
                    )
                    # Or adjacent numeric segments
                    is_num_num_pair = any(c.isdigit() for c in s1["text"]) and any(c.isdigit() for c in t2)

                    if is_label_num_pair or is_num_num_pair:
                        if y_delta >= 2.0:
                            pair_key = (s1["text"], s2["text"])
                            if pair_key not in seen_pairs:
                                seen_pairs.add(pair_key)
                                baseline_anomalies.append({
                                    "text_left": s1["text"],
                                    "text_right": s2["text"],
                                    "baseline_delta_px": round(y_delta, 2),
                                    "bbox_normalized": [
                                        round(min(s1["bbox"][1], s2["bbox"][1]) / height, 4),
                                        round(min(s1["bbox"][0], s2["bbox"][0]) / width, 4),
                                        round(max(s1["bbox"][3], s2["bbox"][3]) / height, 4),
                                        round(max(s1["bbox"][2], s2["bbox"][2]) / width, 4),
                                    ]
                                })

    doc.close()

    is_consistent = (
        len(invisible_spans) == 0 and
        len(baseline_anomalies) == 0 and
        len(injected_prompts) == 0
    )

    return {
        "page_number": page_number,
        "total_spans": total_spans,
        "is_consistent": is_consistent,
        "invisible_spans": invisible_spans,
        "injected_prompts": injected_prompts,
        "baseline_anomalies": baseline_anomalies,
    }

def crosscheck_document_text_layers(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Runs text layer crosscheck across all pages in a document.
    """
    doc = pymupdf.open(pdf_path)
    page_count = len(doc)
    doc.close()

    results = []
    for page_num in range(1, page_count + 1):
        page_res = crosscheck_page_text_layers(pdf_path, page_num)
        results.append(page_res)
    return results
