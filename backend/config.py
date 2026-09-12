import os
from pathlib import Path

try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseSettings
    except ImportError:
        class BaseSettings:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "AI College Learning Assistant"
    BASE_DIR: Path = BASE_DIR
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "college-ai-super-secret-key-production-grade-2026")
    
    # Database configuration
    # Default to sqlite:///./college_ai.db for instant zero-dependency execution
    # Can be overridden by setting DATABASE_URL in environment (e.g. postgresql://user:pass@localhost:5432/college_ai)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'college_ai.db'}")
    
    # Dataset file paths
    COURSE_ENGAGEMENT_PATH: str = os.getenv(
        "COURSE_ENGAGEMENT_PATH", 
        r"C:\Users\Pranjal\Downloads\student_course_engagement.xlsx"
    )
    HACKATHON_SUBMISSIONS_PATH: str = os.getenv(
        "HACKATHON_SUBMISSIONS_PATH", 
        r"C:\Users\Pranjal\Downloads\Untitled spreadsheet.xlsx"
    )
    
    # Knowledge Base directory for RAG
    KNOWLEDGE_BASE_DIR: str = str(BASE_DIR / "data" / "knowledge_base")
    
    # AI / LLM configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
