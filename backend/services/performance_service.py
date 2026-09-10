import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from backend.models.db_models import AssessmentQuestionResult, AssessmentAttempt, CourseEngagement, StudentCourse
from backend.models.schemas import (
    TopicPerformance, DifficultyPerformance, LearningEfficiencyDetail, 
    EngagementPerformanceInsight, StudentPerformanceSummary
)

logger = logging.getLogger("PerformanceService")

class PerformanceService:
    def get_topic_performance(self, db: Session, student_id: str) -> List[TopicPerformance]:
        """
        Calculates topic-level accuracy strictly from actual student question results.
        Formula: Accuracy = (Total Score Obtained / Total Possible Score) * 100
        Weakness criteria: Accuracy < 60% OR Failed questions >= 2.
        """
        rows = db.query(
            AssessmentQuestionResult.topic,
            func.coalesce(AssessmentQuestionResult.skill, "General").label("skill"),
            func.count(AssessmentQuestionResult.id).label("total_q"),
            func.sum(AssessmentQuestionResult.obtained_score).label("total_obtained"),
            func.sum(AssessmentQuestionResult.question_score).label("total_possible"),
            func.sum(case((AssessmentQuestionResult.status == 'pass', 1), else_=0)).label("passed"),
            func.sum(case((AssessmentQuestionResult.status == 'fail', 1), else_=0)).label("failed")
        ).filter(
            AssessmentQuestionResult.student_id == student_id
        ).group_by(
            AssessmentQuestionResult.topic,
            AssessmentQuestionResult.skill
        ).all()

        results = []
        for r in rows:
            tot_obtained = float(r.total_obtained or 0.0)
            tot_possible = float(r.total_possible or 0.0)
            acc = round((tot_obtained / tot_possible * 100.0), 1) if tot_possible > 0 else 0.0
            failed_count = int(r.failed or 0)
            is_weak = (acc < 60.0) or (failed_count >= 2)

            results.append(TopicPerformance(
                topic=str(r.topic),
                skill=str(r.skill),
                total_questions=int(r.total_q),
                passed_count=int(r.passed or 0),
                failed_count=failed_count,
                obtained_score=tot_obtained,
                max_score=tot_possible,
                accuracy_percentage=acc,
                is_weak=is_weak
            ))

        # Sort with lowest accuracy first
        results.sort(key=lambda x: (x.accuracy_percentage, -x.failed_count))
        return results

    def get_weak_topics(self, db: Session, student_id: str) -> List[TopicPerformance]:
        """
        Returns only topics flagged as weak, ordered by severity.
        """
        all_topics = self.get_topic_performance(db, student_id)
        return [t for t in all_topics if t.is_weak]

    def get_difficulty_performance(self, db: Session, student_id: str) -> List[DifficultyPerformance]:
        """
        Calculates student accuracy across question difficulty tiers (easy, medium, hard).
        """
        rows = db.query(
            AssessmentQuestionResult.difficulty,
            func.count(AssessmentQuestionResult.id).label("total_q"),
            func.sum(AssessmentQuestionResult.obtained_score).label("total_obtained"),
            func.sum(AssessmentQuestionResult.question_score).label("total_possible")
        ).filter(
            AssessmentQuestionResult.student_id == student_id
        ).group_by(
            AssessmentQuestionResult.difficulty
        ).all()

        results = []
        for r in rows:
            diff = str(r.difficulty).lower().strip()
            tot_obtained = float(r.total_obtained or 0.0)
            tot_possible = float(r.total_possible or 0.0)
            acc = round((tot_obtained / tot_possible * 100.0), 1) if tot_possible > 0 else 0.0
            results.append(DifficultyPerformance(
                difficulty=diff,
                total_questions=int(r.total_q),
                accuracy_percentage=acc
            ))

        # Order by standard difficulty order: easy, medium, hard
        order = {"easy": 1, "medium": 2, "hard": 3}
        results.sort(key=lambda x: order.get(x.difficulty, 99))
        return results

    def calculate_learning_efficiency(
        self, 
        overall_accuracy: float, 
        avg_course_progress: float, 
        resource_engagement_ratio: float, 
        consistency_ratio: float
    ) -> LearningEfficiencyDetail:
        """
        Phase 6: Optional Learning Efficiency Score (0 to 100)
        Documented formula:
        Score = 0.40 * Assessment Accuracy + 0.30 * Course Progress + 0.20 * Resource Engagement + 0.10 * Consistency
        """
        raw_score = (
            0.40 * overall_accuracy + 
            0.30 * avg_course_progress + 
            0.20 * (resource_engagement_ratio * 100.0) + 
            0.10 * (consistency_ratio * 100.0)
        )
        score = int(round(min(100.0, max(0.0, raw_score))))

        grade = "High Efficiency" if score >= 75 else ("Moderate Efficiency" if score >= 50 else "Needs Improvement")
        
        explanation = (
            f"Your score of {score}/100 is computed from your assessment accuracy ({overall_accuracy:.1f}%, weight 40%), "
            f"course syllabus progress ({avg_course_progress:.1f}%, weight 30%), resource engagement "
            f"({resource_engagement_ratio*100:.1f}%, weight 20%), and completion consistency ({consistency_ratio*100:.1f}%, weight 10%)."
        )

        return LearningEfficiencyDetail(
            score=score,
            grade=grade,
            formula_summary="0.40*Accuracy + 0.30*Progress + 0.20*ResourceEngagement + 0.10*Consistency",
            factors={
                "accuracy_contribution": round(0.40 * overall_accuracy, 1),
                "progress_contribution": round(0.30 * avg_course_progress, 1),
                "resource_contribution": round(0.20 * resource_engagement_ratio * 100.0, 1),
                "consistency_contribution": round(0.10 * consistency_ratio * 100.0, 1)
            },
            explanation=explanation
        )

    def analyze_engagement_vs_performance(
        self, 
        tot_views: int, 
        tot_resources: int, 
        overall_accuracy: float
    ) -> EngagementPerformanceInsight:
        """
        Phase 5: Engagement vs Assessment Performance Diagnostics.
        Compares high/low engagement against high/low performance.
        """
        is_high_engagement = (tot_views >= 5) or (tot_resources >= 10)
        is_high_performance = overall_accuracy >= 65.0

        if is_high_engagement and not is_high_performance:
            quadrant = "High Engagement, Low Assessment Accuracy"
            summary = "Your course engagement is high, but assessment accuracy is comparatively low."
            reasoning = (
                f"You have logged {tot_views} views and {tot_resources} resource interactions, "
                f"yet your assessment accuracy is {overall_accuracy:.1f}%. This indicates diligent time investment "
                "that needs to be converted into deeper conceptual mastery."
            )
            strategy = "Focus on targeted practice questions and active recall rather than passive reading."
        elif not is_high_engagement and is_high_performance:
            quadrant = "Low Engagement, High Assessment Accuracy"
            summary = "High test performance achieved with minimal platform interaction."
            reasoning = (
                f"Your assessment accuracy is strong at {overall_accuracy:.1f}%, despite modest engagement "
                f"({tot_views} views, {tot_resources} resource clicks). You possess solid prior subject knowledge."
            )
            strategy = "Take advanced assessments and dive directly into higher difficulty challenge problems."
        elif is_high_engagement and is_high_performance:
            quadrant = "High Engagement, High Assessment Accuracy"
            summary = "Excellent balance of persistent engagement and top-tier accuracy."
            reasoning = (
                f"Your consistent learning routine ({tot_views} views, {tot_resources} resource clicks) is yielding "
                f"strong results ({overall_accuracy:.1f}% accuracy)."
            )
            strategy = "Continue at your current pace and prepare for capstone hackathon assessments."
        else:
            quadrant = "Low Engagement, Low Assessment Accuracy"
            summary = "Both platform engagement and assessment accuracy require structured revitalization."
            reasoning = (
                f"Engagement is nascent ({tot_views} views, {tot_resources} resource clicks) and accuracy "
                f"stands at {overall_accuracy:.1f}%."
            )
            strategy = "Begin with foundational video lessons, review weak topics, and take 5-question beginner quizzes."

        return EngagementPerformanceInsight(
            quadrant=quadrant,
            summary=summary,
            detailed_reasoning=reasoning,
            recommended_strategy=strategy
        )

    def get_student_performance(self, db: Session, student_id: str) -> StudentPerformanceSummary:
        """
        Compiles the full performance summary for the student.
        """
        topics = self.get_topic_performance(db, student_id)
        weak_topics = [t for t in topics if t.is_weak]
        diff_perf = self.get_difficulty_performance(db, student_id)

        # Overall question stats
        q_totals = db.query(
            func.count(AssessmentQuestionResult.id),
            func.sum(AssessmentQuestionResult.obtained_score),
            func.sum(AssessmentQuestionResult.question_score)
        ).filter(
            AssessmentQuestionResult.student_id == student_id
        ).first()

        tot_q = int(q_totals[0] or 0)
        tot_obt = float(q_totals[1] or 0.0)
        tot_pos = float(q_totals[2] or 0.0)
        overall_acc = round((tot_obt / tot_pos * 100.0), 1) if tot_pos > 0 else 0.0

        tot_assessments = db.query(func.count(AssessmentAttempt.attempt_id)).filter(
            AssessmentAttempt.student_id == student_id
        ).scalar() or 0

        # Engagement stats for efficiency score & insights
        eng_stats = db.query(
            func.coalesce(func.sum(CourseEngagement.total_views), 0),
            func.coalesce(func.sum(CourseEngagement.resource_clicks_downloads), 0)
        ).filter(CourseEngagement.student_id == student_id).first()
        tot_views = int(eng_stats[0]) if eng_stats else 0
        tot_res = int(eng_stats[1]) if eng_stats else 0

        # Course progress
        courses_count = db.query(func.count(StudentCourse.id)).filter(StudentCourse.student_id == student_id).scalar() or 0
        cert_count = db.query(func.count(StudentCourse.id)).filter(
            StudentCourse.student_id == student_id,
            StudentCourse.certificate_issued == True
        ).scalar() or 0
        
        avg_progress = 50.0 if courses_count > 0 else 0.0
        if courses_count > 0 and cert_count > 0:
            avg_progress = min(100.0, avg_progress + (cert_count / courses_count) * 50.0)

        res_ratio = min(1.0, tot_res / 20.0)
        consistency_ratio = min(1.0, tot_q / 50.0)

        efficiency = self.calculate_learning_efficiency(
            overall_accuracy=overall_acc,
            avg_course_progress=avg_progress,
            resource_engagement_ratio=res_ratio,
            consistency_ratio=consistency_ratio
        )

        insights = self.analyze_engagement_vs_performance(
            tot_views=tot_views,
            tot_resources=tot_res,
            overall_accuracy=overall_acc
        )

        return StudentPerformanceSummary(
            student_id=student_id,
            overall_accuracy_percentage=overall_acc,
            total_questions_attempted=tot_q,
            total_assessments_completed=tot_assessments,
            weak_topics=weak_topics,
            all_topics=topics,
            difficulty_breakdown=diff_perf,
            learning_efficiency=efficiency,
            engagement_vs_performance=insights
        )

performance_service = PerformanceService()
