import logging
from typing import Dict, Any, List, Optional
from backend.rag.vector_store import vector_store

logger = logging.getLogger("RAGService")

class RAGService:
    def __init__(self):
        self.store = vector_store

    def retrieve_course_knowledge(
        self,
        query: str,
        top_k: int = 3,
        course_filter: Optional[str] = None,
        topic_filter: Optional[str] = None,
        min_similarity_threshold: float = 0.35
    ) -> Dict[str, Any]:
        """
        Retrieves relevant course content chunks using semantic similarity and metadata filtering.
        Enforces strict hallucination guardrails: if no chunks meet threshold, explicitly signals insufficient data.
        """
        raw_results = self.store.search(
            query=query,
            top_k=top_k,
            course_filter=course_filter,
            topic_filter=topic_filter
        )

        filtered = [r for r in raw_results if r["score"] >= min_similarity_threshold]

        if not filtered:
            return {
                "has_sufficient_info": False,
                "chunks": [],
                "context": "",
                "sources": [],
                "refusal_message": "I couldn't find sufficient information in the available course material."
            }

        sources = list(dict.fromkeys([r["source"] for r in filtered])) # deduplicate maintaining order
        context_parts = []
        for idx, r in enumerate(filtered):
            context_parts.append(f"--- SOURCE [{idx+1}]: {r['source']} ---\n{r['text']}")

        return {
            "has_sufficient_info": True,
            "chunks": filtered,
            "context": "\n\n".join(context_parts),
            "sources": sources,
            "refusal_message": None
        }

rag_service = RAGService()
