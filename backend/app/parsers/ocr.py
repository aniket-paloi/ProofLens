import re
import pymupdf
from typing import List, Dict, Any, Optional, Tuple

def extract_page_tokens(pdf_path: str, page_number: int) -> Dict[str, Any]:
    """
    Extracts text words, blocks, and normalized geometries from a PDF page.
    page_number is 1-indexed.
    """
    doc = pymupdf.open(pdf_path)
    if page_number < 1 or page_number > len(doc):
        doc.close()
        raise ValueError(f"Page number {page_number} out of range (1..{len(doc)})")
    
    page = doc[page_number - 1]
    width = page.rect.width
    height = page.rect.height

    raw_words = page.get_text("words") # (x0, y0, x1, y1, word, block_no, line_no, word_no)
    tokens = []
    
    for idx, (x0, y0, x1, y1, word, block_no, line_no, word_no) in enumerate(raw_words):
        # Normalize to [ymin, xmin, ymax, xmax] in [0.0, 1.0]
        ymin = round(max(0.0, min(1.0, y0 / height)), 4)
        xmin = round(max(0.0, min(1.0, x0 / width)), 4)
        ymax = round(max(0.0, min(1.0, y1 / height)), 4)
        xmax = round(max(0.0, min(1.0, x1 / width)), 4)

        tokens.append({
            "token_id": idx,
            "text": word,
            "bbox_original": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
            "bbox_normalized": [ymin, xmin, ymax, xmax],
            "block_no": block_no,
            "line_no": line_no,
            "word_no": word_no,
        })

    raw_text = page.get_text("text")
    doc.close()

    return {
        "page_number": page_number,
        "width_pts": width,
        "height_pts": height,
        "raw_text": raw_text,
        "tokens": tokens,
    }

def find_phrase_bbox(pdf_path: str, page_number: int, phrase: str) -> Optional[Dict[str, Any]]:
    """
    Finds the exact normalized bounding box of a phrase using PyMuPDF vector search.
    """
    doc = pymupdf.open(pdf_path)
    page = doc[page_number - 1]
    width = page.rect.width
    height = page.rect.height

    rects = page.search_for(phrase)
    doc.close()

    if not rects:
        return None

    # Enclosing bounding box of matches
    r = rects[0]
    for other in rects[1:]:
        r = r | other

    ymin = round(max(0.0, min(1.0, r.y0 / height)), 4)
    xmin = round(max(0.0, min(1.0, r.x0 / width)), 4)
    ymax = round(max(0.0, min(1.0, r.y1 / height)), 4)
    xmax = round(max(0.0, min(1.0, r.x1 / width)), 4)

    return {
        "text": phrase,
        "bbox_original": [round(r.x0, 2), round(r.y0, 2), round(r.x1, 2), round(r.y1, 2)],
        "bbox_normalized": [ymin, xmin, ymax, xmax]
    }

def clean_currency_str(val_str: str) -> Optional[float]:
    """Extracts numeric float from currency string (e.g. 'INR 1,20,000.00' -> 120000.0)."""
    cleaned = re.sub(r"[^\d.]", "", val_str)
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None

