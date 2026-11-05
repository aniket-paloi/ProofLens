import io
import hashlib
from typing import Tuple, Dict, Any
import pymupdf

# Allowed content signatures (magic bytes)
MAGIC_SIGNATURES = {
    b"%PDF-": "application/pdf",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
}

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
MAX_PAGE_COUNT = 50
MAX_PIXELS = 25_000_000  # 25 megapixels per page

class DocumentValidationError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message

def detect_mime_type(file_bytes: bytes) -> str:
    for signature, mime in MAGIC_SIGNATURES.items():
        if file_bytes.startswith(signature):
            return mime
    raise DocumentValidationError(
        code="UNSUPPORTED_MIME_TYPE",
        message="Unsupported file format. Only PDF, PNG, and JPEG documents are permitted."
    )

def validate_and_inspect_document(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    # 1. Size check
    file_size = len(file_bytes)
    if file_size == 0:
        raise DocumentValidationError(code="EMPTY_FILE", message="Uploaded file is empty (0 bytes).")
    if file_size > MAX_FILE_SIZE_BYTES:
        raise DocumentValidationError(
            code="FILE_TOO_LARGE",
            message=f"File size {file_size} bytes exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES} bytes."
        )

    # 2. Content signature verification
    mime_type = detect_mime_type(file_bytes)
    sha256 = hashlib.sha256(file_bytes).hexdigest()

    # 3. Parsability & encryption check
    page_count = 1
    if mime_type == "application/pdf":
        try:
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            raise DocumentValidationError(
                code="CORRUPT_DOCUMENT",
                message=f"PDF document is corrupt or unparsable: {str(e)}"
            )

        if doc.is_encrypted:
            doc.close()
            raise DocumentValidationError(
                code="ENCRYPTED_PDF_UNSUPPORTED",
                message="Password-protected or encrypted PDFs are unsupported. Please decrypt before uploading."
            )

        page_count = len(doc)
        if page_count == 0:
            doc.close()
            raise DocumentValidationError(code="EMPTY_PDF", message="PDF document contains zero pages.")
        if page_count > MAX_PAGE_COUNT:
            doc.close()
            raise DocumentValidationError(
                code="PAGE_LIMIT_EXCEEDED",
                message=f"Document has {page_count} pages, which exceeds the maximum limit of {MAX_PAGE_COUNT}."
            )
        doc.close()

    return {
        "filename": filename,
        "mime_type": mime_type,
        "file_size_bytes": file_size,
        "sha256_hash": sha256,
        "page_count": page_count
    }

