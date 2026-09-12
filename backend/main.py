import os
import sys
from pathlib import Path

# Ensure project root is in sys.path so 'backend' package is always resolvable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database.connection import init_db
from backend.rag.vector_store import vector_store
from backend.api import (
    routes_student,
    routes_performance,
    routes_assessment,
    routes_practice,
    routes_assistant
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("CollegeAI")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    init_db()
    logger.info("Loading / verifying vector store index...")
    vector_store.build_or_load_index()
    logger.info(f"{settings.APP_NAME} backend started successfully.")
    yield
    logger.info("Shutting down backend...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade AI College Learning Assistant combining structured data, RAG, deterministic rules, and analytics.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api/v1
app.include_router(routes_student.router, prefix=settings.API_V1_STR)
app.include_router(routes_performance.router, prefix=settings.API_V1_STR)
app.include_router(routes_assessment.router, prefix=settings.API_V1_STR)
app.include_router(routes_practice.router, prefix=settings.API_V1_STR)
app.include_router(routes_assistant.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    reload = os.environ.get("RELOAD", "false").lower() in ("true", "1")
    uvicorn.run("backend.main:app", host=host, port=port, reload=reload, app_dir=str(PROJECT_ROOT))
