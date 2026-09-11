import re
from typing import Dict, Any, List, Optional

class SessionMemory:
    def __init__(self):
        # Maps conversation_id -> conversation state
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get_or_create_session(self, conversation_id: str) -> Dict[str, Any]:
        if conversation_id not in self.sessions:
            self.sessions[conversation_id] = {
                "messages": [],
                "last_weak_topics": [],
                "last_discussed_topic": None,
                "last_discussed_course": None,
                "last_discussed_assessment_id": None
            }
        return self.sessions[conversation_id]

    def resolve_query(self, query: str, conversation_id: str) -> Dict[str, Any]:
        """
        Phase 11: Conversational Memory & Contextual Follow-ups
        Resolves ambiguous pronouns like 'the first one', 'it', 'the second topic'
        using previously established entities.
        """
        session = self.get_or_create_session(conversation_id)
        resolved_query = query
        resolved_topic = None
        q_low = query.lower()

        last_weak = session.get("last_weak_topics", [])
        last_topic = session.get("last_discussed_topic")

        # 1. Resolve "the first one" / "first topic"
        if re.search(r"\b(the\s+)?first(\s+one|\s+topic)?\b", q_low):
            if last_weak and len(last_weak) > 0:
                resolved_topic = last_weak[0]
                resolved_query = re.sub(r"\b(the\s+)?first(\s+one|\s+topic)?\b", resolved_topic, resolved_query, flags=re.IGNORECASE)

        # 2. Resolve "the second one" / "second topic"
        elif re.search(r"\b(the\s+)?second(\s+one|\s+topic)?\b", q_low):
            if last_weak and len(last_weak) > 1:
                resolved_topic = last_weak[1]
                resolved_query = re.sub(r"\b(the\s+)?second(\s+one|\s+topic)?\b", resolved_topic, resolved_query, flags=re.IGNORECASE)

        # 3. Resolve "it" / "that topic" / "on it" / "about it"
        elif re.search(r"\b(explain\s+it|about\s+it|on\s+it|practice\s+it|questions\s+on\s+it)\b", q_low):
            target = last_topic or (last_weak[0] if last_weak else None)
            if target:
                resolved_topic = target
                resolved_query = resolved_query.replace(" it", f" {target}").replace(" It", f" {target}")

        if resolved_topic:
            session["last_discussed_topic"] = resolved_topic

        return {
            "original_query": query,
            "resolved_query": resolved_query,
            "resolved_topic": resolved_topic,
            "last_topic": last_topic
        }

    def update_session(
        self,
        conversation_id: str,
        user_message: str,
        assistant_reply: str,
        weak_topics: Optional[List[str]] = None,
        discussed_topic: Optional[str] = None,
        assessment_id: Optional[int] = None
    ):
        session = self.get_or_create_session(conversation_id)
        session["messages"].append({"role": "user", "content": user_message})
        session["messages"].append({"role": "assistant", "content": assistant_reply})

        if weak_topics:
            session["last_weak_topics"] = weak_topics
            if not session["last_discussed_topic"] and len(weak_topics) > 0:
                session["last_discussed_topic"] = weak_topics[0]

        if discussed_topic:
            session["last_discussed_topic"] = discussed_topic

        if assessment_id is not None:
            session["last_discussed_assessment_id"] = assessment_id

memory = SessionMemory()
