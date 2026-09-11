import os
import logging
from typing import Optional, List, Dict, Any
from backend.config import settings

logger = logging.getLogger("LLMClient")

class LLMClient:
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        self.provider = "deterministic"

        if self.gemini_key:
            self.provider = "gemini"
            logger.info("Configured Google Gemini LLM provider.")
        elif self.openai_key:
            self.provider = "openai"
            logger.info("Configured OpenAI LLM provider.")
        else:
            logger.info("Using Deterministic Academic Synthesizer (offline mode, zero external API dependencies).")

    def generate_response(
        self,
        prompt: str,
        system_instruction: str = "You are an AI College Learning Assistant.",
        context_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Synthesizes a response using Gemini, OpenAI, or the Deterministic Synthesizer.
        """
        if self.provider == "gemini" and self.gemini_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.gemini_key)
                full_prompt = f"{system_instruction}\n\n{prompt}"
                response = client.models.generate_content(
                    model=settings.LLM_MODEL,
                    contents=full_prompt
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini generation error: {e}. Falling back to deterministic synthesizer.")

        elif self.provider == "openai" and self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )
                if response.choices and response.choices[0].message.content:
                    return response.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"OpenAI generation error: {e}. Falling back to deterministic synthesizer.")

        # Deterministic Academic Synthesizer
        return self._deterministic_synthesis(prompt, context_data)

    def _deterministic_synthesis(self, prompt: str, context_data: Optional[Dict[str, Any]]) -> str:
        """
        Grounded rule-based synthesis for guaranteed deterministic responses without hallucinations.
        """
        if not context_data:
            return "I have processed your query. Please refer to your student performance dashboard or ask for specific course explanations."

        intent = context_data.get("intent", "")

        # 1. Weak Topics Intent
        if intent == "weak_topics":
            weak = context_data.get("weak_topics", [])
            if not weak:
                return "Congratulations! You do not currently have any topics with accuracy below 60%. All your attempted topics show satisfactory proficiency."
            
            top = weak[0]
            other_names = [w["topic"] for w in weak[1:3]]
            others_str = f" as well as {', '.join(other_names)}" if other_names else ""
            return (
                f"Based on your actual assessment submissions, your primary weak topic is **{top['topic']}** "
                f"with an accuracy of **{top['accuracy_percentage']}%** ({top['failed_count']} failed question(s) "
                f"out of {top['total_questions']} attempted){others_str}.\n\n"
                f"Would you like me to explain {top['topic']} or generate 5 practice questions to help you improve?"
            )

        # 2. Performance Overview Intent
        if intent == "performance":
            perf = context_data.get("performance", {})
            acc = perf.get("overall_accuracy_percentage", 0.0)
            tot_q = perf.get("total_questions_attempted", 0)
            eff = perf.get("learning_efficiency", {}).get("score", 0)
            return (
                f"### Performance Summary\n"
                f"- **Overall Assessment Accuracy**: {acc}%\n"
                f"- **Total Questions Attempted**: {tot_q}\n"
                f"- **Learning Efficiency Score**: {eff}/100\n\n"
                f"Your assessment performance indicates areas of strength as well as specific topics requiring revision."
            )

        # 3. Assessment Eligibility Intent
        if intent == "assessment_eligibility":
            elig = context_data.get("eligibility", {})
            title = elig.get("title", "Assessment")
            is_elig = elig.get("eligible", False)
            reqs = elig.get("requirements", [])
            reasons = elig.get("reasons", [])

            lines = [f"### Assessment Eligibility: {title}"]
            lines.append(f"**Status**: {'ELIGIBLE' if is_elig else 'NOT ELIGIBLE'}\n")
            lines.append("**Requirements Verification:**")
            for r in reqs:
                symbol = "✓" if r["satisfied"] else "✗"
                lines.append(f"- [{symbol}] **{r['name']}**: {r['detail']}")

            if not is_elig and reasons:
                lines.append("\n**Reasons for Failure:**")
                for reason in reasons:
                    lines.append(f"- {reason}")
            elif is_elig:
                lines.append("\nYou satisfy all prerequisites and may proceed to take this assessment.")

            return "\n".join(lines)

        # 4. Concept Explanation (RAG)
        if intent == "course_concept":
            rag = context_data.get("rag", {})
            if not rag.get("has_sufficient_info", False):
                return "I couldn't find sufficient information in the available course material to answer your question."

            chunks = rag.get("chunks", [])
            sources = rag.get("sources", [])
            main_content = chunks[0]["text"] if chunks else ""
            source_list = "\n".join([f"- {s}" for s in sources])

            return (
                f"### Concept Explanation\n\n"
                f"{main_content}\n\n"
                f"---\n"
                f"**Sources Used:**\n{source_list}"
            )

        # 5. Study Coach Recommendation
        if intent == "study_coach":
            rec = context_data.get("recommendation", {})
            return (
                f"### AI Study Coach Recommendation\n\n"
                f"- **Priority Topic**: {rec.get('priority_topic')}\n"
                f"- **Reason**: {rec.get('reason')}\n"
                f"- **Recommended Action**: {rec.get('recommended_action')}\n"
                f"- **Relevant Course Material**: {rec.get('relevant_course_material')}\n"
                f"- **Practice Recommendation**: {rec.get('practice_recommendation')}"
            )

        # Default fallback
        return (
            "I have retrieved your academic data and course knowledge. "
            "Please let me know if you would like performance insights, weak topic breakdowns, or course concept explanations."
        )

llm_client = LLMClient()
