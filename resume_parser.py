"""Module 1 & 2 - resume upload validation and text extraction (in memory only)."""
import io
import os

import docx
from pypdf import PdfReader

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_MB = 5


class ResumeError(Exception):
    """Raised for invalid or unreadable resumes."""


def validate_file(filename: str, size_bytes: int) -> None:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ResumeError("Unsupported file type. Please upload a PDF or DOCX resume.")
    if size_bytes > MAX_FILE_MB * 1024 * 1024:
        raise ResumeError(f"File is larger than {MAX_FILE_MB} MB.")
    if size_bytes == 0:
        raise ResumeError("The file is empty.")


def extract_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    return "\n".join((page.extract_text() or "") for page in reader.pages)  # every page


def extract_docx(data: bytes) -> str:
    document = docx.Document(io.BytesIO(data))
    parts = [p.text for p in document.paragraphs]  # every paragraph
    for table in document.tables:  # resumes often put skills in tables
        for row in table.rows:
            parts.extend(cell.text for cell in row.cells)
    return "\n".join(parts)


def extract_text(filename: str, data: bytes) -> str:
    """Validate and extract raw text. Nothing is written to disk."""
    validate_file(filename, len(data))
    ext = os.path.splitext(filename)[1].lower()
    try:
        text = extract_pdf(data) if ext == ".pdf" else extract_docx(data)
    except Exception as exc:  # corrupt or encrypted files
        raise ResumeError(f"Could not read the file: {exc}") from exc
    if len(text.strip()) < 30:
        raise ResumeError("Very little text found. Scanned/image resumes need OCR (not supported).")
    return text
