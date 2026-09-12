import os
import re
import math
import json
import logging
from collections import Counter
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from backend.config import settings
from backend.rag.chunker import DocumentChunker

logger = logging.getLogger("VectorStore")

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", 
    "by", "can", "did", "do", "does", "doing", "don", "down", "during", "each", "few", "for", 
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", 
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", 
    "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", 
    "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she", 
    "should", "so", "some", "such", "t", "than", "that", "the", "their", "theirs", "them", 
    "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too", 
    "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which", 
    "while", "who", "whom", "why", "will", "with", "you", "your", "yours", "yourself", "yourselves"
}

def _tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [w for w in words if len(w) > 1 and w not in STOPWORDS]

class LocalVectorStore:
    def __init__(self, kb_dir: Optional[str] = None):
        self.kb_dir = kb_dir or settings.KNOWLEDGE_BASE_DIR
        self.cache_dir = Path(settings.BASE_DIR) / "data" / "rag_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.chunks_file = self.cache_dir / "chunks.json"
        self.embeddings_file = self.cache_dir / "embeddings.npy"

        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        self.dfs: Counter = Counter()
        self.model = None

    def _get_model(self):
        # Cloud environments (like Render Free Tier 512MB RAM) get killed if PyTorch loads.
        # Guard against OOM by defaulting to lightweight, high-precision BM25.
        if os.getenv("RENDER") or os.getenv("LOW_MEMORY_MODE", "").lower() in ("true", "1"):
            return None

        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}...")
                self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer: {e}. Falling back to BM25.")
                self.model = None
        return self.model

    def build_or_load_index(self, force_rebuild: bool = False):
        if not force_rebuild and self.chunks_file.exists() and self.embeddings_file.exists():
            try:
                with open(self.chunks_file, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
                self.embeddings = np.load(self.embeddings_file)
                self._index_tokens()
                logger.info(f"Loaded {len(self.chunks)} cached vector chunks from {self.cache_dir}")
                return
            except Exception as e:
                logger.warning(f"Failed loading cache: {e}. Rebuilding index...")

        chunker = DocumentChunker(self.kb_dir)
        self.chunks = chunker.load_and_chunk()
        self._index_tokens()
        logger.info(f"Extracted {len(self.chunks)} chunks from knowledge base.")

    def _index_tokens(self):
        self.dfs = Counter()
        for c in self.chunks:
            tokens = _tokenize(f"{c.get('topic', '')} {c.get('topic', '')} {c.get('course', '')} {c.get('text', '')}")
            c["_tokens"] = tokens
            for t in set(tokens):
                self.dfs[t] += 1

    def search(
        self, 
        query: str, 
        top_k: int = 3, 
        course_filter: Optional[str] = None, 
        topic_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if not self.chunks or (self.embeddings is None and not self.dfs):
            self.build_or_load_index()

        if not self.chunks:
            return []

        model = self._get_model()
        if model is not None and self.embeddings is not None:
            q_vec = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
            similarities = np.dot(self.embeddings, q_vec)
        else:
            # Memory-safe, high-speed BM25 search (<0.1ms, zero PyTorch overhead)
            if not self.dfs:
                self._index_tokens()

            N = max(1, len(self.chunks))
            q_tokens = _tokenize(query)
            avgdl = max(1.0, sum(len(c.get("_tokens", [])) for c in self.chunks) / N)
            k1 = 1.5
            b = 0.75

            similarities = []
            for c in self.chunks:
                tokens = c.get("_tokens")
                if tokens is None:
                    tokens = _tokenize(f"{c.get('topic', '')} {c.get('topic', '')} {c.get('course', '')} {c.get('text', '')}")
                    c["_tokens"] = tokens

                doc_len = len(tokens)
                counts = Counter(tokens)
                raw_score = 0.0
                for t in q_tokens:
                    if t in self.dfs:
                        idf = math.log((N - self.dfs[t] + 0.5) / (self.dfs[t] + 0.5) + 1.0)
                        f = counts[t]
                        tf = (f * (k1 + 1.0)) / (f + k1 * (1.0 - b + b * (doc_len / avgdl)))
                        if t in str(c.get("topic", "")).lower():
                            tf *= 2.0
                        raw_score += idf * tf

                norm_score = min(1.0, raw_score / 10.0)
                similarities.append(norm_score)

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
