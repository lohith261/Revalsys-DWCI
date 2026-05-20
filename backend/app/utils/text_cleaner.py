import re
from typing import List


def clean_text(raw_text: str) -> str:
    """Clean and normalize extracted text."""
    # Fix common encoding artifacts
    text = raw_text.replace('\x00', '')
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Remove excessive whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove excessive newlines (more than 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    # Final strip
    text = text.strip()
    return text


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks by words."""
    words = text.split()
    if len(words) <= chunk_size:
        return [text] if text else []

    chunks = []
    step = chunk_size - chunk_overlap
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunks.append(' '.join(chunk_words))
        if end == len(words):
            break
        start += step
    return chunks
