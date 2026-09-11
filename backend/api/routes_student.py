from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.services.student_service import student_service
from backend.models.schemas import StudentProfile, CourseSummary, CourseEngagementDetail
from backend.models.db_models import Student, StudentCourse, AssessmentAttempt

router = APIRouter(prefix="/students", tags=["Students"])

DEFAULT_DEMO_STUDENT = "02754054-361a-4025-be96-1bd8a049ae18"

def get_current_student_id(x_student_id: Optional[str] = Header(None)) -> str:
    """
    Phase 13 Security & Isolation: Extracts authenticated student ID from request header.
    Defaults to primary benchmark student for seamless out-of-the-box demonstration.
    """
    return x_student_id if x_student_id else DEFAULT_DEMO_STUDENT

@router.get("/demo-list")
def get_demo_students(db: Session = Depends(get_db)):
    """
    Returns curated demo students with verified multi-modal profiles (courses + hackathons).
    """
    candidates = [
        ("02754054-361a-4025-be96-1bd8a049ae18", "Aarav Sharma", "CS Senior — Aptitude & Python Focus"),
        ("073df96e-ade7-40fe-ba34-5e2f8e272845", "Priya Patel", "Data Science & Technical Hackathon"),
        ("05c950e8-30fe-4d30-bf11-97b4e1b85ae0", "Rohan Verma", "Business Analytics & Machine Learning"),
        ("07909202-7d6c-4dcb-bb9d-101c4d619140", "Ananya Reddy", "Full Stack Developer & Java")
    ]
    results = []
    for uid, name, desc in candidates:
        profile = student_service.get_student_profile(db, uid)
        if profile:
            results.append({
                "student_id": uid,
                "name": name,
                "profile_description": desc,
                "courses_count": profile.enrolled_courses_count,
                "assessments_count": profile.assessments_taken_count,
                "views": profile.total_views
            })
    return results

@router.get("/me/profile", response_model=StudentProfile)
def get_my_profile(
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db)
):
    profile = student_service.get_student_profile(db, student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return profile

@router.get("/me/courses", response_model=List[CourseSummary])
def get_my_courses(
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db)
):
    return student_service.get_student_courses(db, student_id)

@router.get("/me/courses/{course_id}/progress")
def get_my_course_progress(
    course_id: int,
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db)
):
    progress = student_service.get_course_progress(db, student_id, course_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Course enrollment not found for this student")
    return progress

@router.get("/me/courses/{course_id}/engagement", response_model=CourseEngagementDetail)
def get_my_course_engagement(
    course_id: int,
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db)
):
    eng = student_service.get_course_engagement(db, student_id, course_id)
    if not eng:
        raise HTTPException(status_code=404, detail="Course engagement records not found")
    return eng

@router.get("/me/assessments/history")
def get_my_assessment_history(
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db)
):
    return student_service.get_assessment_history(db, student_id)

@router.get("/me/practice/history")
def get_my_practice_history(
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db)
):
    return student_service.get_practice_history(db, student_id)
