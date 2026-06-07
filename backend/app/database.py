import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# DATABASE URL SETUP & FALLBACK
# ==========================================
# We fetch DATABASE_URL from .env.
# If not specified, we fall back to SQLite (a file-based local database).
# This allows the app to work out-of-the-box for beginners!
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sqlite_study_app.db")

# SQLite needs a specific argument to allow multi-threaded access.
# We check if the URL starts with sqlite to apply this parameter safely.
is_sqlite = DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

# Create the SQLAlchemy Engine
# The engine is responsible for maintaining connection pools and talking to the DB.
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Create a SessionLocal class
# Each instance of SessionLocal will be a single database transaction session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ==========================================
# BASE CLASS FOR MODELS
# ==========================================
# We inherit from this class to define our database models (tables).
Base = declarative_base()

# ==========================================
# DEPENDENCY INJECTION: GET DB SESSION
# ==========================================
# This function is used as a FastAPI dependency.
# It opens a database connection session for a single request,
# yields (passes) it to the route handler,
# and automatically closes it when the request is finished.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
