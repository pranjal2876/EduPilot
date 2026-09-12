from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.api.routes_student import get_current_student_id
from backend.models.schemas import ChatRequest, ChatResponse
from backend.ai.orchestrator import ai_orchestrator

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])

@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(
    req: ChatRequest,
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db)
):
    """
    Phase 8 AI Orchestrator & Phase 15 Transparency:
    Orchestrates intent routing, controlled database retrieval, RAG, and business logic execution.
    Exposes tool provenance and source citations.
    """
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Query message cannot be empty.")

    try:
        return ai_orchestrator.process_message(
            db=db,
            student_id=student_id,
            message=req.message.strip(),
            conversation_id=req.conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration error: {str(e)}")

@router.get("/scenarios")
def get_evaluation_scenarios():
    """
    Phase 14 & 15: Golden Evaluation Scenarios
    Returns the 20 benchmark test scenarios for live system verification and compliance auditing.
    """
    import json
    from pathlib import Path
    scenarios_path = Path(__file__).resolve().parent.parent / "evaluation" / "scenarios.json"
    if scenarios_path.exists():
        with open(scenarios_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
