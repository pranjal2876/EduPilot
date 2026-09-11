from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.api.routes_student import get_current_student_id
from backend.services.performance_service import performance_service
from backend.services.study_coach_service import study_coach_service
from backend.models.schemas import StudentPerformanceSummary, TopicPerformance

router = APIRouter(prefix="/performance", tags=["Performance & Analytics"])

@router.get("/me", response_model=StudentPerformanceSummary)
def get_my_performance(
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db)
):
    return performance_service.get_student_performance(db, student_id)

@router.get("/me/weak-topics", response_model=List[TopicPerformance])
def get_my_weak_topics(
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db)
):
    return performance_service.get_weak_topics(db, student_id)

@router.get("/me/topics", response_model=List[TopicPerformance])
def get_my_topic_performance(
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db)
):
    return performance_service.get_topic_performance(db, student_id)

@router.get("/me/recommendation")
def get_my_study_recommendation(
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db)
):
    return study_coach_service.get_study_recommendation(db, student_id)
