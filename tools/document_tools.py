"""
tools/document_tools.py
========================
Raw OCR/PDF extraction helpers used by Agent 1.
These are plain functions (not @tool) because Agent 1
calls them deterministically inside extract_documents_node.
"""

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
import easyocr


def extract_pdf_text(pdf_path: str) -> str:
    loader = PyPDFLoader(pdf_path)
    docs   = loader.load()
    return "\n".join(doc.page_content for doc in docs)


def extract_image_text(image_path: str) -> str:
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_path)
    return "\n".join([res[1] for res in result])


def extract_text(path: str) -> str:
    """Routes to PDF or image extractor based on file extension."""
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return extract_pdf_text(path)
    elif ext in [".jpg", ".jpeg", ".png"]:
        return extract_image_text(path)
    else:
        raise ValueError(f"Unsupported format: {ext}")
