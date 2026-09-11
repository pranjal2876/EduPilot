from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.api.routes_student import get_current_student_id
from backend.models.schemas import (
    PracticeQuizRequest, PracticeQuizResponse, PracticeSubmissionRequest, PracticeSubmissionResult
)
from backend.services.practice_service import practice_service

router = APIRouter(prefix="/practice", tags=["Personalized Practice"])

@router.post("/generate", response_model=PracticeQuizResponse)
def generate_quiz(req: PracticeQuizRequest):
    """
    Phase 10: Generates quiz questions grounded strictly in retrieved course content.
    """
    try:
        return practice_service.generate_practice_quiz(
            topic=req.topic,
            course_name=req.course_name or "General",
            difficulty=req.difficulty,
            num_questions=req.num_questions
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@router.post("/submit", response_model=PracticeSubmissionResult)
def submit_quiz(
    req: PracticeSubmissionRequest,
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db)
):
    """
    Evaluates submitted answers, records score in practice history, and returns feedback.
    """
    try:
        return practice_service.submit_practice_quiz(
            db=db,
            student_id=student_id,
            submission=req
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Submission evaluation error: {str(e)}")
