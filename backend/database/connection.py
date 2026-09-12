import gzip
import shutil
import logging
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from backend.config import settings
from backend.models.db_models import Base

logger = logging.getLogger("Database")

def ensure_database_extracted():
    if settings.DATABASE_URL.startswith("sqlite"):
        db_path_str = settings.DATABASE_URL.replace("sqlite:///", "")
        db_path = Path(db_path_str)
        if not db_path.is_absolute():
            db_path = Path(settings.BASE_DIR) / db_path

        gz_candidates = [
            Path(settings.BASE_DIR) / "data" / "college_ai.db.gz",
            Path(settings.BASE_DIR) / "college_ai.db.gz"
        ]

        if not db_path.exists() or db_path.stat().st_size < 100000:
            for gz_file in gz_candidates:
                if gz_file.exists():
                    logger.info(f"Extracting compressed database from {gz_file} to {db_path}...")
                    db_path.parent.mkdir(parents=True, exist_ok=True)
                    with gzip.open(gz_file, "rb") as f_in:
                        with open(db_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    logger.info(f"Successfully extracted {db_path.name} ({db_path.stat().st_size} bytes)")
                    break

ensure_database_extracted()

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

# Enable foreign keys pragma for SQLite
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
