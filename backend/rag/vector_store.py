import os
import json
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from backend.config import settings
from backend.rag.chunker import DocumentChunker

logger = logging.getLogger("VectorStore")

class LocalVectorStore:
    def __init__(self, kb_dir: Optional[str] = None):
        self.kb_dir = kb_dir or settings.KNOWLEDGE_BASE_DIR
        self.cache_dir = Path(settings.BASE_DIR) / "data" / "rag_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.chunks_file = self.cache_dir / "chunks.json"
        self.embeddings_file = self.cache_dir / "embeddings.npy"

        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        self.model = None

    def _get_model(self):
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}...")
                self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer: {e}. Falling back to TF-IDF/bag-of-words.")
                self.model = None
        return self.model

    def build_or_load_index(self, force_rebuild: bool = False):
        if not force_rebuild and self.chunks_file.exists() and self.embeddings_file.exists():
            try:
                with open(self.chunks_file, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
                self.embeddings = np.load(self.embeddings_file)
                logger.info(f"Loaded {len(self.chunks)} cached vector chunks from {self.cache_dir}")
                return
            except Exception as e:
                logger.warning(f"Failed loading cache: {e}. Rebuilding index...")

        chunker = DocumentChunker(self.kb_dir)
        self.chunks = chunker.load_and_chunk()
        logger.info(f"Extracted {len(self.chunks)} chunks from knowledge base.")

        if not self.chunks:
            return

        texts = [c["text"] for c in self.chunks]
        model = self._get_model()

        if model is not None:
            vectors = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            self.embeddings = vectors
        else:
            # Fallback simple deterministic feature hashing representation
            dim = 384
            vecs = []
            for t in texts:
                v = np.zeros(dim, dtype=np.float32)
                for w in t.lower().split():
                    h = hash(w) % dim
                    v[h] += 1.0
                norm = np.linalg.norm(v)
                if norm > 0:
                    v /= norm
                vecs.append(v)
            self.embeddings = np.array(vecs, dtype=np.float32)

        # Cache to disk
        with open(self.chunks_file, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, indent=2)
        np.save(self.embeddings_file, self.embeddings)
        logger.info("Successfully indexed and saved vector embeddings.")

    def search(
        self, 
        query: str, 
        top_k: int = 3, 
        course_filter: Optional[str] = None, 
        topic_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if not self.chunks or self.embeddings is None:
            self.build_or_load_index()

        if not self.chunks or self.embeddings is None:
            return []

        model = self._get_model()
        if model is not None:
            q_vec = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
        else:
            dim = 384
            q_vec = np.zeros(dim, dtype=np.float32)
            for w in query.lower().split():
                h = hash(w) % dim
                q_vec[h] += 1.0
            norm = np.linalg.norm(q_vec)
            if norm > 0:
                q_vec /= norm

        # Compute cosine similarity
        similarities = np.dot(self.embeddings, q_vec)

        results = []
        for idx, score in enumerate(similarities):
            chunk = self.chunks[idx]

            # Metadata filtering
            if course_filter:
                cf = course_filter.lower()
                c_name = chunk["course"].lower()
                c_domain = chunk["domain"].lower()
                if cf not in c_name and cf not in c_domain:
                    continue

            if topic_filter:
                tf_words = [w for w in topic_filter.lower().split() if len(w) > 2]
                match = any(w in chunk["topic"].lower() or w in chunk["text"].lower() or w in chunk["course"].lower() for w in tf_words)
                if not match:
                    continue

            results.append({
                "chunk_id": chunk["chunk_id"],
                "course": chunk["course"],
                "domain": chunk["domain"],
                "sub_domain": chunk["sub_domain"],
                "topic": chunk["topic"],
                "source": chunk["source"],
                "score": float(score),
                "text": chunk["raw_content"]
            })

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

vector_store = LocalVectorStore()
