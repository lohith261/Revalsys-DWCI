import io
import uuid
from datetime import datetime
from typing import List, Tuple

import pdfplumber
from docx import Document

from app.config import get_settings
from app.utils.text_cleaner import clean_text, chunk_text


class DocumentProcessor:
    def __init__(self):
        self.settings = get_settings()

    def extract_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF using pdfplumber."""
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    def extract_docx(self, file_bytes: bytes) -> str:
        """Extract text from DOCX."""
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)

    def process_file(self, file_bytes: bytes, filename: str) -> Tuple[str, str, List[str]]:
        """Process uploaded file: extract, clean, chunk."""
        file_id = str(uuid.uuid4())
        ext = filename.lower().split('.')[-1]

        if ext == 'pdf':
            raw_text = self.extract_pdf(file_bytes)
        elif ext == 'docx':
            raw_text = self.extract_docx(file_bytes)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        cleaned = clean_text(raw_text)
        chunks = chunk_text(
            cleaned,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap
        )

        return file_id, cleaned, chunks
