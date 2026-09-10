import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.services.performance_service import performance_service
from backend.services.student_service import student_service

logger = logging.getLogger("StudyCoachService")

class StudyCoachService:
    def get_study_recommendation(self, db: Session, student_id: str) -> Dict[str, Any]:
        """
        Phase 4: AI Study Coach
        Analyzes actual student performance and engagement to produce a factual, grounded next-step study recommendation.
        Returns:
            - priority_topic
            - reason (never fabricated)
            - recommended_action
            - relevant_course_material
            - practice_recommendation
        """
        weak_topics = performance_service.get_weak_topics(db, student_id)
        courses = student_service.get_student_courses(db, student_id)

        if not weak_topics:
            # Check if student has attempted questions
            all_topics = performance_service.get_topic_performance(db, student_id)
            if not all_topics:
                # Student has not attempted any assessments yet
                return {
                    "priority_topic": "Foundational Aptitude & Programming",
                    "reason": "You have not yet completed any assessment questions in your enrolled subjects.",
                    "recommended_action": "Begin by reviewing the introductory lessons in your enrolled courses and attempt an initial practice quiz.",
                    "relevant_course_material": "Enrolled Courses: " + (", ".join([c.course_title for c in courses[:3]]) if courses else "General Curriculum"),
                    "practice_recommendation": "Complete 5 easy practice questions to establish a baseline proficiency score."
                }
            else:
                # All topics have >= 60% accuracy!
                best_topic = all_topics[-1]
                return {
                    "priority_topic": best_topic.topic,
                    "reason": f"You have achieved solid proficiency (>=60% accuracy) across all {len(all_topics)} attempted topics. Your highest scoring topic is {best_topic.topic} ({best_topic.accuracy_percentage}%).",
                    "recommended_action": f"Advance your problem-solving velocity by attempting hard-level practice quizzes in {best_topic.topic}.",
                    "relevant_course_material": f"Advanced modules related to {best_topic.skill} / {best_topic.topic}.",
                    "practice_recommendation": f"Complete 5 hard practice questions in {best_topic.topic} to prepare for competitive hackathon benchmarks."
                }

        # Select primary priority topic (lowest accuracy, highest failure count)
        top_weak = weak_topics[0]
        acc = top_weak.accuracy_percentage
        tot_q = top_weak.total_questions
        failed = top_weak.failed_count

        reason = (
            f"Your current accuracy in '{top_weak.topic}' is {acc:.1f}% across {tot_q} attempted question(s), "
            f"with {failed} recorded failure(s), making it your lowest-performing subject area."
        )

        # Map to relevant course material
        relevant_material = f"Course Curriculum: {top_weak.skill} → Module on {top_weak.topic}"
        for c in courses:
            if top_weak.topic.lower() in c.course_title.lower() or top_weak.topic.lower() in c.course_sub_domain.lower():
                relevant_material = f"{c.course_title} (Domain: {c.course_domain}, Sub-Domain: {c.course_sub_domain})"
                break

        action = (
            f"Review the core theoretical notes and worked examples for '{top_weak.topic}'. "
            "Focus specifically on formula application and fundamental error patterns before retaking tests."
        )

        practice_rec = f"Complete 5 medium practice questions in '{top_weak.topic}' to reinforce conceptual understanding."

        return {
            "priority_topic": top_weak.topic,
            "skill": top_weak.skill,
            "accuracy_percentage": acc,
            "total_questions": tot_q,
            "failed_count": failed,
            "reason": reason,
            "recommended_action": action,
            "relevant_course_material": relevant_material,
            "practice_recommendation": practice_rec,
            "coach_summary": (
                f"Your current priority is {top_weak.topic} because your recent accuracy in this topic ({acc:.1f}%) "
                f"is lower than your performance in other attempted topics. Review the relevant material and complete 5 medium practice questions."
            )
        }

study_coach_service = StudyCoachService()
