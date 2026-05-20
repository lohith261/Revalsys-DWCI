"""
End-to-end test flow for Document Web Chat Intelligence System.

Prerequisites:
- Backend running (default: http://localhost:8000)
- Redis running
- OPENAI_API_KEY set in environment

Run with: pytest backend/tests/test_flow.py -v
"""

import os
import sys
import time
import uuid
import requests
from io import BytesIO

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from docx import Document

BASE_URL = os.getenv("API_BASE", "http://localhost:8000")
API = f"{BASE_URL}/api/v1"


def create_sample_docx() -> bytes:
    """Create a sample DOCX file with known content."""
    doc = Document()
    doc.add_heading("Acme Corp Annual Report 2024", 0)
    doc.add_paragraph(
        "Acme Corporation reported record revenue of $500 million in fiscal year 2024. "
        "The company's primary revenue driver is its cloud infrastructure division, which grew by 45%. "
        "CEO Jane Doe highlighted the expansion into the European market as a key strategic win. "
        "Operating margin improved to 22%, up from 18% in the prior year. "
        "Headcount grew to 3,200 employees across 12 global offices."
    )
    doc.add_heading("Product Highlights", level=1)
    doc.add_paragraph(
        "The flagship product, AcmeCloud, now serves over 10,000 enterprise customers. "
        "New AI-powered analytics modules were launched in Q3 and contributed $30M in new ARR. "
        "Customer satisfaction score (NPS) reached an all-time high of 72."
    )
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.read()


def test_health():
    r = requests.get(f"{API}/health")
    assert r.status_code == 200
    data = r.json()
    assert data["redis"] is True
    assert data["vector_db"] is True
    print("[PASS] Health check")


def test_upload():
    session_id = str(uuid.uuid4())
    docx_bytes = create_sample_docx()
    files = {"file": ("sample_report.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    data = {"session_id": session_id}
    r = requests.post(f"{API}/upload", data=data, files=files)
    assert r.status_code == 200, r.text
    resp = r.json()
    assert resp["file_name"] == "sample_report.docx"
    assert resp["chunks_indexed"] > 0
    assert resp["status"] == "processed"
    print(f"[PASS] Upload: {resp['file_id']} with {resp['chunks_indexed']} chunks")
    return session_id, resp["file_id"]


def test_chat_document(session_id: str, file_id: str):
    payload = {
        "query": "What was Acme Corporation's revenue in 2024?",
        "session_id": session_id,
        "file_ids": [file_id],
    }
    r = requests.post(f"{API}/chat", json=payload)
    assert r.status_code == 200, r.text
    resp = r.json()
    assert resp["source"] == "document"
    assert resp["cached"] is False
    assert len(resp["referenced_files"]) > 0
    assert "500" in resp["answer"] or "million" in resp["answer"].lower()
    print(f"[PASS] Document Q1: source={resp['source']}, cached={resp['cached']}")
    return resp


def test_chat_followup(session_id: str, file_id: str):
    payload = {
        "query": "Who is the CEO?",
        "session_id": session_id,
        "file_ids": [file_id],
    }
    r = requests.post(f"{API}/chat", json=payload)
    assert r.status_code == 200, r.text
    resp = r.json()
    assert resp["source"] == "document"
    assert "Jane Doe" in resp["answer"] or "CEO" in resp["answer"]
    print(f"[PASS] Document Q2 (follow-up): source={resp['source']}")


def test_chat_cache(session_id: str, file_id: str):
    payload = {
        "query": "What was Acme Corporation's revenue in 2024?",
        "session_id": session_id,
        "file_ids": [file_id],
    }
    r = requests.post(f"{API}/chat", json=payload)
    assert r.status_code == 200, r.text
    resp = r.json()
    assert resp["cached"] is True
    print(f"[PASS] Cache hit: cached={resp['cached']}")


def test_chat_web_fallback():
    session_id = str(uuid.uuid4())
    payload = {
        "query": "What is the weather like on Mars today?",
        "session_id": session_id,
    }
    r = requests.post(f"{API}/chat", json=payload)
    assert r.status_code == 200, r.text
    resp = r.json()
    assert resp["source"] == "web"
    assert resp["cached"] is False
    print(f"[PASS] Web fallback: source={resp['source']}")


def test_session_history(session_id: str):
    r = requests.get(f"{API}/session/{session_id}")
    assert r.status_code == 200, r.text
    resp = r.json()
    assert resp["session_id"] == session_id
    assert len(resp["messages"]) > 0
    print(f"[PASS] Session history: {len(resp['messages'])} messages")


def test_delete_session(session_id: str):
    r = requests.delete(f"{API}/session/{session_id}")
    assert r.status_code == 200, r.text
    print("[PASS] Session deleted")


def run_all():
    print("=" * 60)
    print("Document Web Chat Intelligence - End-to-End Test Flow")
    print("=" * 60)

    test_health()
    session_id, file_id = test_upload()
    test_chat_document(session_id, file_id)
    test_chat_followup(session_id, file_id)
    test_chat_cache(session_id, file_id)
    test_chat_web_fallback()
    test_session_history(session_id)
    test_delete_session(session_id)

    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    run_all()
