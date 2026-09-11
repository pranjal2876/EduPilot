from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.api.routes_student import get_current_student_id
from backend.models.db_models import Assessment, Course
from backend.models.schemas import AssessmentEligibilityResponse
from backend.business_logic.rule_engine import rule_engine

router = APIRouter(prefix="/assessments", tags=["Assessments & Business Rules"])

@router.get("/list")
def list_assessments(db: Session = Depends(get_db)):
    """
    Returns curated assessment offerings for the student assessment catalog.
    """
    # Order so our benchmark assessments appear first
    benchmark_ids = [341, 901, 902, 999]
    top_records = db.query(Assessment).filter(Assessment.assessment_id.in_(benchmark_ids)).all()
    other_records = db.query(Assessment).filter(~Assessment.assessment_id.in_(benchmark_ids)).limit(20).all()

    combined = top_records + other_records
    results = []
    for a in combined:
        prereq_name = None
        if a.prerequisite_course_id:
            c = db.query(Course).filter(Course.course_id == a.prerequisite_course_id).first()
            prereq_name = c.course_title if c else f"Course #{a.prerequisite_course_id}"

        results.append({
            "assessment_id": a.assessment_id,
            "title": a.title,
            "domain": a.domain,
            "sub_domain": a.sub_domain,
            "num_questions": a.num_questions,
            "passing_score": a.passing_score,
            "max_attempts": a.max_attempts,
            "is_active": a.is_active,
            "prerequisite_course_id": a.prerequisite_course_id,
            "prerequisite_course_name": prereq_name
        })
    return results

@router.get("/{assessment_id}/eligibility", response_model=AssessmentEligibilityResponse)
def check_eligibility(
    assessment_id: int,
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db)
):
    """
    Phase 9 Business Rules: Evaluates student eligibility against deterministic rules.
    """
    return rule_engine.check_assessment_eligibility(db, student_id, assessment_id)
