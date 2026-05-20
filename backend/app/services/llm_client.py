from typing import List, Dict, Any, Optional

from openai import OpenAI

from app.config import get_settings


class LLMClient:
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(
            api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_base_url,
        )
        self.model = self.settings.llm_model

    def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Generate a response using OpenAI-compatible API."""
        formatted = [{"role": "system", "content": system_prompt}]
        formatted.extend(messages)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=formatted,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    def build_document_prompt(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        history: List[Dict[str, Any]],
    ) -> tuple:
        """Build system prompt and messages for document-based answer."""
        context = "\n\n---\n\n".join(
            [f"[Document: {c['metadata']['file_name']}]\n{c['content']}" for c in chunks]
        )

        system = (
            "You are a helpful document assistant. Use ONLY the provided document context to answer. "
            "If the context doesn't contain the answer, say so. Cite document names when possible. "
            "Be concise but thorough."
        )

        history_text = ""
        for msg in history:
            prefix = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{prefix}: {msg['content']}\n"

        user_prompt = (
            f"Previous conversation:\n{history_text}\n"
            f"Document context:\n{context}\n\n"
            f"Question: {query}\n\nAnswer:"
        )

        return system, [{"role": "user", "content": user_prompt}]

    def build_web_prompt(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        history: List[Dict[str, Any]],
    ) -> tuple:
        """Build system prompt and messages for web-based answer."""
        context = "\n\n---\n\n".join(
            [
                f"[Source: {r['title']} - {r['href']}]\n{r['body']}"
                for r in search_results
            ]
        )

        system = (
            "You are a helpful assistant. Use the provided web search results to answer. "
            "Synthesize the information and include citations to sources. Be concise but thorough."
        )

        history_text = ""
        for msg in history:
            prefix = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{prefix}: {msg['content']}\n"

        user_prompt = (
            f"Previous conversation:\n{history_text}\n"
            f"Web search results:\n{context}\n\n"
            f"Question: {query}\n\nAnswer:"
        )

        return system, [{"role": "user", "content": user_prompt}]
