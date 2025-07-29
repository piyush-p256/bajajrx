import os
import requests
import tempfile
from typing import List, Dict
from pathlib import Path
from urllib.parse import urlparse
from pypdf import PdfReader
# from docx import Document as DocxDocument  # Uncomment when implementing DOCX
# import extract_msg  # Uncomment when implementing email parsing


def download_file(url: str, dest_folder: str = None) -> str:
    """
    Download a file from a URL and return the local file path.
    """
    if dest_folder is None:
        dest_folder = tempfile.gettempdir()
    os.makedirs(dest_folder, exist_ok=True)
    local_filename = os.path.join(dest_folder, os.path.basename(urlparse(url).path))
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return local_filename


def detect_file_type(file_path: str) -> str:
    """
    Detect file type based on extension. Returns 'pdf', 'docx', or 'email'.
    """
    ext = Path(file_path).suffix.lower()
    if ext == '.pdf':
        return 'pdf'
    elif ext == '.docx':
        return 'docx'
    elif ext in ['.eml', '.msg']:
        return 'email'
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def parse_pdf(file_path: str) -> List[Dict]:
    """
    Parse a PDF file and return a list of text chunks with metadata.
    Each chunk is a dict: { 'text': ..., 'metadata': {...} }
    """
    reader = PdfReader(file_path)
    chunks = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            chunk = {
                'text': text.strip(),
                'metadata': {
                    'source': file_path,
                    'page_number': i + 1
                }
            }
            chunks.append(chunk)
    return chunks


def parse_docx(file_path: str) -> List[Dict]:
    """
    Placeholder for DOCX parsing. To be implemented.
    """
    # doc = DocxDocument(file_path)
    # ...
    return []


def parse_email(file_path: str) -> List[Dict]:
    """
    Placeholder for email parsing. To be implemented.
    """
    # ...
    return []


def ingest_document(url: str) -> List[Dict]:
    """
    Download, detect type, parse, and chunk. Return all chunks.
    """
    file_path = download_file(url)
    file_type = detect_file_type(file_path)
    if file_type == 'pdf':
        return parse_pdf(file_path)
    elif file_type == 'docx':
        return parse_docx(file_path)
    elif file_type == 'email':
        return parse_email(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}") 