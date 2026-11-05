import os
import uuid
from pathlib import Path
from typing import List, Dict, Any
import pymupdf
from PIL import Image
from backend.app.core.config import settings

def render_and_route_pages(original_path: str, mime_type: str) -> List[Dict[str, Any]]:
    pages_meta: List[Dict[str, Any]] = []
    
    if mime_type == "application/pdf":
        doc = pymupdf.open(original_path)
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_num = page_idx + 1
            rect = page.rect
            width = float(rect.width)
            height = float(rect.height)
            rotation = int(page.rotation)

            # Page-level routing: Check if native text exists
            text_content = page.get_text("text").strip()
            has_native_text = 1 if len(text_content) > 15 else 0

            # Render 150 DPI derivative PNG for viewer & visual analysis
            zoom = 150 / 72.0
            mat = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            page_id = str(uuid.uuid4())
            render_filename = f"{page_id}.png"
            render_full_path = settings.DERIVATIVES_DIR / "pages" / render_filename
            pix.save(str(render_full_path))

            pages_meta.append({
                "page_id": page_id,
                "page_number": page_num,
                "width_pts": width,
                "height_pts": height,
                "rotation_deg": rotation,
                "has_native_text": has_native_text,
                "rendered_image_path": str(render_full_path),
                "native_text_preview": text_content[:200] if has_native_text else ""
            })
        doc.close()

    elif mime_type in ["image/png", "image/jpeg"]:
        # Handle standalone image document
        page_id = str(uuid.uuid4())
        render_filename = f"{page_id}.png"
        render_full_path = settings.DERIVATIVES_DIR / "pages" / render_filename
        
        with Image.open(original_path) as img:
            width, height = img.size
            # Convert and save as PNG derivative
            img.convert("RGB").save(str(render_full_path), format="PNG")

        pages_meta.append({
            "page_id": page_id,
            "page_number": 1,
            "width_pts": float(width),
            "height_pts": float(height),
            "rotation_deg": 0,
            "has_native_text": 0,  # Raster images have no native vector text
            "rendered_image_path": str(render_full_path),
            "native_text_preview": ""
        })

    return pages_meta

