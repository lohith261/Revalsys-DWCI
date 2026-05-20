import os
import uuid
from typing import List, Dict, Optional

from app.config import get_settings


class VectorStore:
    def __init__(self):
        self.settings = get_settings()
        self.persist_dir = os.path.join(os.getcwd(), "chroma_data")
        os.makedirs(self.persist_dir, exist_ok=True)
        # Lazy imports to avoid slow startup on Render
        import chromadb
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(name="documents")
        self._model = None

    @property
    def model(self):
        """Lazy-load the embedding model to avoid blocking app startup."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.settings.embedding_model)
        return self._model

    def index_chunks(self, file_id: str, file_name: str, chunks: List[str]) -> int:
        """Index document chunks into vector store."""
        if not chunks:
            return 0

        embeddings = self.model.encode(chunks).tolist()
        ids = [f"{file_id}_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "file_id": file_id,
                "file_name": file_name,
                "chunk_index": i,
                "chunk_id": ids[i],
            }
            for i in range(len(chunks))
        ]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )
        return len(chunks)

    def search(
        self,
        query: str,
        top_k: int = 5,
        file_ids: Optional[List[str]] = None,
    ) -> List[Dict]:
        """Search vector store for relevant chunks."""
        query_embedding = self.model.encode([query]).tolist()

        where_filter = None
        if file_ids:
            where_filter = {"file_id": {"$in": file_ids}}

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                # Convert L2 distance to approximate cosine similarity
                similarity = 1.0 / (1.0 + distance)
                hits.append({
                    "chunk_id": doc_id,
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity": similarity,
                })
        return hits

    def delete_by_file_id(self, file_id: str) -> None:
        """Remove all chunks for a given file."""
        self.collection.delete(where={"file_id": file_id})

    def reset(self) -> None:
        """Clear all data."""
        self.client.delete_collection("documents")
        import chromadb
        self.collection = self.client.get_or_create_collection(name="documents")
