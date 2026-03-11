from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

from app.core.config import SUPABASE_URL, SUPABASE_KEY, DATABASE_URL

load_dotenv()
# --------------------------------------------------
# Database URL (Supabase PostgreSQL)
# --------------------------------------------------
# Format:
# postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DATABASE

DATABASE_URL = os.getenv("DATABASE_URL")


# --------------------------------------------------
# SQLAlchemy Engine & Session
# --------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    # This line is CRITICAL for the Supabase Transaction Pooler
    # It prevents "prepared statement" errors
    prepared_statement_cache_size=0,
    connect_args={
        "options": "-c statement_timeout=30000",
        # Some versions of psycopg2 also need this in connect_args
        "client_encoding": "utf8"
    },
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)




# --------------------------------------------------
# Dependency
# --------------------------------------------------

def get_db():
    """
    FastAPI dependency that provides a database session.
    Ensures the session is closed after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
