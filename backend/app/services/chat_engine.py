from datetime import datetime
from typing import List, Optional, Dict, Any

from app.config import get_settings
from app.services.vector_store import VectorStore
from app.services.redis_cache import RedisCache
from app.services.llm_client import LLMClient
from app.services.web_search import WebSearch


class ChatEngine:
    def __init__(
        self,
        vector_store: VectorStore,
        redis_cache: RedisCache,
        llm_client: LLMClient,
        web_search: WebSearch,
    ):
        self.vector_store = vector_store
        self.redis_cache = redis_cache
        self.llm_client = llm_client
        self.web_search = web_search
        self.settings = get_settings()

    def run(
        self,
        query: str,
        session_id: str,
        file_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        7-Step Query Pipeline:
        1. Receive Request
        2. Cache Check
        3. Document Retrieval
        4. Response Generation
        5. Source Labeling
        6. Cache Storage
        7. Return Response
        """
        # Step 1: Receive Request (already parsed)
        query_hash = self.redis_cache.hash_query(query)

        # Step 2: Cache Check
        cached = self.redis_cache.get_cached_response(query_hash, session_id, file_ids)
        if cached:
            cached["cached"] = True
            cached["session_id"] = session_id
            # Still log this query to session history
            self.redis_cache.add_session_message(session_id, "user", query)
            self.redis_cache.add_session_message(session_id, "assistant", cached["answer"], cached["source"])
            return cached

        # Get conversation history for context
        history = self.redis_cache.get_session_history(session_id)

        # Step 3: Document Retrieval
        hits = self.vector_store.search(
            query, top_k=5, file_ids=file_ids if file_ids else None
        )
        relevant_chunks = [h for h in hits if h["similarity"] >= self.settings.similarity_threshold]

        # Step 4: Response Generation
        if relevant_chunks:
            system_prompt, messages = self.llm_client.build_document_prompt(
                query, relevant_chunks, history
            )
            answer = self.llm_client.generate(system_prompt, messages)
            source = "document"
            referenced_files = []
            seen = set()
            for chunk in relevant_chunks:
                fid = chunk["metadata"]["file_id"]
                fname = chunk["metadata"]["file_name"]
                if fid not in seen:
                    seen.add(fid)
                    referenced_files.append({
                        "file_id": fid,
                        "file_name": fname,
                        "relevance_score": round(chunk["similarity"], 4),
                    })
        else:
            # Web search fallback
            web_results = self.web_search.search(query, max_results=3)
            system_prompt, messages = self.llm_client.build_web_prompt(
                query, web_results, history
            )
            answer = self.llm_client.generate(system_prompt, messages)
            source = "web"
            referenced_files = []

        # Step 5: Source Labeling is done above

        # Build response payload
        response_payload = {
            "answer": answer,
            "source": source,
            "session_id": session_id,
            "cached": False,
            "referenced_files": referenced_files,
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Step 6: Cache Storage
        self.redis_cache.set_cached_response(
            query_hash, session_id, file_ids, response_payload
        )

        # Update session history
        self.redis_cache.add_session_message(session_id, "user", query)
        self.redis_cache.add_session_message(session_id, "assistant", answer, source)

        # Step 7: Return Response
        return response_payload
