import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.db_models import Student, Course, StudentCourse, CourseEngagement, AssessmentAttempt, PracticeHistory
from backend.models.schemas import StudentProfile, CourseSummary, CourseEngagementDetail

logger = logging.getLogger("StudentService")

class StudentService:
    def get_student_profile(self, db: Session, student_id: str) -> Optional[StudentProfile]:
        """
        Retrieves top-level profile information for a student.
        Validates existence and aggregates enrollment & assessment counts.
        """
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return None

        enrolled_count = db.query(func.count(StudentCourse.id)).filter(StudentCourse.student_id == student_id).scalar() or 0
        assessments_count = db.query(func.count(AssessmentAttempt.attempt_id)).filter(AssessmentAttempt.student_id == student_id).scalar() or 0
        
        # Aggregate engagement totals
        eng_stats = db.query(
            func.coalesce(func.sum(CourseEngagement.total_views), 0),
            func.coalesce(func.sum(CourseEngagement.resource_clicks_downloads), 0)
        ).filter(CourseEngagement.student_id == student_id).first()
        
        tot_views = int(eng_stats[0]) if eng_stats else 0
        tot_resources = int(eng_stats[1]) if eng_stats else 0
        
        cert_count = db.query(func.count(StudentCourse.id)).filter(
            StudentCourse.student_id == student_id,
            StudentCourse.certificate_issued == True
        ).scalar() or 0

        return StudentProfile(
            student_id=student.student_id,
            enrolled_courses_count=enrolled_count,
            assessments_taken_count=assessments_count,
            total_views=tot_views,
            total_resource_clicks=tot_resources,
            certificates_earned=cert_count
        )

    def get_student_courses(self, db: Session, student_id: str) -> List[CourseSummary]:
        """
        Returns list of all courses the student is enrolled in with progress calculations.
        """
        results = db.query(StudentCourse, Course, CourseEngagement).join(
            Course, StudentCourse.course_id == Course.course_id
        ).outerjoin(
            CourseEngagement, 
            (StudentCourse.student_id == CourseEngagement.student_id) & 
            (StudentCourse.course_id == CourseEngagement.course_id)
        ).filter(
            StudentCourse.student_id == student_id
        ).all()

        summaries = []
        for sc, course, ce in results:
            # Deterministic course progress formula:
            # If certificate issued: 100%
            # Otherwise: min(100%, ((views + resource_clicks) / total_activities) * 100%)
            tot_acts = course.total_activities if course.total_activities > 0 else 50
            if sc.certificate_issued:
                progress = 100.0
            elif ce:
                progress = min(100.0, round(((ce.total_views + ce.resource_clicks_downloads) / tot_acts) * 100.0, 1))
            else:
                progress = 0.0

            summaries.append(CourseSummary(
                course_id=course.course_id,
                course_title=course.course_title,
                course_domain=course.course_domain,
                course_sub_domain=course.course_sub_domain,
                course_level=course.course_level,
                course_hours=course.course_hours,
                enrolled_at=sc.enrolled_at.strftime("%Y-%m-%d %H:%M:%S") if sc.enrolled_at else None,
                progress_percentage=progress,
                certificate_issued=sc.certificate_issued,
                certificate_link=sc.certificate_link
            ))

        return summaries

    def get_course_progress(self, db: Session, student_id: str, course_id: int) -> Optional[Dict[str, Any]]:
        """
        Calculates detailed progress for a specific student and course.
        """
        sc = db.query(StudentCourse).filter(
            StudentCourse.student_id == student_id,
            StudentCourse.course_id == course_id
        ).first()

        if not sc:
            return None

        course = db.query(Course).filter(Course.course_id == course_id).first()
        ce = db.query(CourseEngagement).filter(
            CourseEngagement.student_id == student_id,
            CourseEngagement.course_id == course_id
        ).first()

        tot_acts = course.total_activities if course and course.total_activities > 0 else 50
        if sc.certificate_issued:
            progress = 100.0
        elif ce:
            progress = min(100.0, round(((ce.total_views + ce.resource_clicks_downloads) / tot_acts) * 100.0, 1))
        else:
            progress = 0.0

        return {
            "student_id": student_id,
            "course_id": course_id,
            "course_title": course.course_title if course else "Unknown",
            "progress_percentage": progress,
            "certificate_issued": sc.certificate_issued,
            "certificate_issued_at": sc.certificate_issued_at.strftime("%Y-%m-%d") if sc.certificate_issued_at else None,
            "total_views": ce.total_views if ce else 0,
            "resource_clicks": ce.resource_clicks_downloads if ce else 0,
            "mcq_attempts": ce.mcq_attempted_count if ce else 0,
            "mcq_score": ce.mcq_total_score_obtained if ce else 0
        }

    def get_course_engagement(self, db: Session, student_id: str, course_id: int) -> Optional[CourseEngagementDetail]:
        """
        Fetches granular course engagement details.
        """
        ce = db.query(CourseEngagement, Course).join(
            Course, CourseEngagement.course_id == Course.course_id
        ).filter(
            CourseEngagement.student_id == student_id,
            CourseEngagement.course_id == course_id
        ).first()

        if not ce:
            return None

        eng, course = ce
        tot_acts = course.total_activities if course.total_activities > 0 else 50
        progress = min(100.0, round(((eng.total_views + eng.resource_clicks_downloads) / tot_acts) * 100.0, 1))

        return CourseEngagementDetail(
            course_id=course.course_id,
            course_title=course.course_title,
            total_views=eng.total_views,
            first_viewed_at=eng.first_viewed_at.strftime("%Y-%m-%d %H:%M:%S") if eng.first_viewed_at else None,
            last_viewed_at=eng.last_viewed_at.strftime("%Y-%m-%d %H:%M:%S") if eng.last_viewed_at else None,
            mcq_attempted_count=eng.mcq_attempted_count,
            mcq_total_score_obtained=eng.mcq_total_score_obtained,
            resource_clicks_downloads=eng.resource_clicks_downloads,
            progress_percentage=progress
        )

    def get_assessment_history(self, db: Session, student_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all past assessment attempts by the student.
        """
        attempts = db.query(AssessmentAttempt).filter(
            AssessmentAttempt.student_id == student_id
        ).order_by(AssessmentAttempt.submitted_at.desc()).all()

        history = []
        for att in attempts:
            history.append({
                "attempt_id": att.attempt_id,
                "assessment_id": att.assessment_id,
                "round_id": att.round_id,
                "submitted_at": att.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if att.submitted_at else None,
                "questions_attempted": att.total_questions_attempted,
                "score_obtained": att.total_score_obtained,
                "possible_score": att.total_possible_score,
                "accuracy_percentage": round(att.accuracy_rate * 100.0, 1),
                "status": att.status
            })
        return history

    def get_practice_history(self, db: Session, student_id: str) -> List[Dict[str, Any]]:
        """
        Returns records of completed practice quizzes.
        """
        practices = db.query(PracticeHistory).filter(
            PracticeHistory.student_id == student_id
        ).order_by(PracticeHistory.completed_at.desc()).all()

        return [
            {
                "id": p.id,
                "topic": p.topic,
                "difficulty": p.difficulty,
                "num_questions": p.num_questions,
                "score_obtained": p.score_obtained,
                "total_score": p.total_score,
                "accuracy_percentage": round(p.accuracy * 100.0, 1),
                "completed_at": p.completed_at.strftime("%Y-%m-%d %H:%M:%S") if p.completed_at else None
            }
            for p in practices
        ]

student_service = StudentService()
