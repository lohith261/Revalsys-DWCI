from typing import List, Dict, Any

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None


class WebSearch:
    def __init__(self):
        pass

    def search(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Search the web using DuckDuckGo."""
        if DDGS is None:
            raise RuntimeError("duckduckgo-search not installed")
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "href": r.get("href", ""),
                    "body": r.get("body", ""),
                })
        return results
