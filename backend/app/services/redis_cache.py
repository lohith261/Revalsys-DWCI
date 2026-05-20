import json
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any

import redis

from app.config import get_settings


class RedisCache:
    def __init__(self):
        self.settings = get_settings()
        self.pool = redis.ConnectionPool.from_url(
            self.settings.redis_url,
            decode_responses=True,
        )
        self.client = redis.Redis(connection_pool=self.pool)

    def _cache_key(self, query_hash: str, session_id: str, file_ids: Optional[List[str]]) -> str:
        file_part = ",".join(sorted(file_ids)) if file_ids else "none"
        return f"cache:{query_hash}:{session_id}:{file_part}"

    def get_cached_response(
        self,
        query_hash: str,
        session_id: str,
        file_ids: Optional[List[str]],
    ) -> Optional[Dict[str, Any]]:
        key = self._cache_key(query_hash, session_id, file_ids)
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None

    def set_cached_response(
        self,
        query_hash: str,
        session_id: str,
        file_ids: Optional[List[str]],
        response: Dict[str, Any],
    ) -> None:
        key = self._cache_key(query_hash, session_id, file_ids)
        self.client.setex(key, self.settings.cache_ttl, json.dumps(response))

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        key = f"session:{session_id}"
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return []

    def add_session_message(
        self,
        session_id: str,
        role: str,
        content: str,
        source: Optional[str] = None,
    ) -> None:
        key = f"session:{session_id}"
        history = self.get_session_history(session_id)
        history.append({
            "role": role,
            "content": content,
            "source": source,
            "timestamp": datetime.utcnow().isoformat(),
        })
        # Trim to max history
        max_msgs = self.settings.max_history_messages
        if len(history) > max_msgs:
            history = history[-max_msgs:]
        self.client.setex(key, self.settings.session_ttl, json.dumps(history))

    def clear_session(self, session_id: str) -> None:
        key = f"session:{session_id}"
        self.client.delete(key)

    def get_session_files(self, session_id: str) -> List[Dict[str, Any]]:
        key = f"session_files:{session_id}"
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return []

    def add_session_file(self, session_id: str, file_meta: Dict[str, Any]) -> None:
        key = f"session_files:{session_id}"
        files = self.get_session_files(session_id)
        files.append(file_meta)
        self.client.setex(key, self.settings.session_ttl, json.dumps(files))

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Return all sessions for sidebar listing."""
        keys = self.client.scan_iter(match="session:*", count=1000)
        sessions = []
        for key in keys:
            if key.startswith("session_files:") or key.startswith("session:") is False:
                continue
            sid = key.replace("session:", "")
            history = self.get_session_history(sid)
            if history:
                first_user_msg = next(
                    (m for m in history if m["role"] == "user"), None
                )
                title = first_user_msg["content"][:60] if first_user_msg else "New Chat"
                sessions.append({
                    "session_id": sid,
                    "title": title,
                    "updated_at": history[-1]["timestamp"],
                })
        return sorted(sessions, key=lambda x: x["updated_at"], reverse=True)

    def health_check(self) -> bool:
        try:
            return self.client.ping()
        except Exception:
            return False

    @staticmethod
    def hash_query(query: str) -> str:
        return hashlib.sha256(query.lower().strip().encode()).hexdigest()
