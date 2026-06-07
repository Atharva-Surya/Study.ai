import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import redis.asyncio as aioredis

from app.logging_config import setup_logging
import time
import logging

# Database imports
from app.database import engine, Base
# We MUST import our models here so SQLAlchemy knows they exist
# before we call create_all!
from app.models.user_model import User
from app.models.item_model import Item
from app.models.flashcard_model import Flashcard
from app.models.quiz_model import QuizQuestion

# Import our custom routers
from app.routes.health import router as health_router
from app.routes.items import router as items_router
from app.routes.auth_routes import router as auth_router
from app.routes.ai_routes import router as ai_router, plain_router as ai_plain_router
from app.routes.rag_routes import router as rag_router

# ==========================================
# DATABASE INITIALIZATION
# ==========================================
# This line checks our database, compares it with our models (User, Item),
# and automatically creates any tables that do not exist yet.
Base.metadata.create_all(bind=engine)

# Load configuration
load_dotenv()

PROJECT_NAME = os.getenv("PROJECT_NAME", "AI Study Assistant")
API_V1_STR = os.getenv("API_V1_STR", "/api/v1")

# Initialize logging
setup_logging()

# Initialize our FastAPI app
app = FastAPI(
    title=PROJECT_NAME,
    description="A modular, production-style API for a student's personal study assistant",
    version="1.0.0",
    docs_url="/docs",  # Swagger documentation
    redoc_url="/redoc" # ReDoc documentation
)

logger = logging.getLogger("app.requests")

@app.middleware("http")
async def log_requests(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    logger.info("%s %s %s %dms", request.method, request.url.path, request.client.host, int(duration))
    return response

# CORS setup
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # React Vite default port
    "http://127.0.0.1:5173",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# REDIS INITIALIZATION
# ==========================================
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

@app.on_event("startup")
async def startup_event():
    try:
        app.state.redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await app.state.redis.ping()
        print("✓ Redis connected")
    except Exception as e:
        print(f"⚠ Redis connection failed: {e}. Continuing without cache.")
        app.state.redis = None

@app.on_event("shutdown")
async def shutdown_event():
    if hasattr(app.state, "redis") and app.state.redis:
        await app.state.redis.close()

# ROUTER REGISTRATION
# Mount routers under /api/v1
app.include_router(health_router, prefix=API_V1_STR)
app.include_router(auth_router, prefix=API_V1_STR)
app.include_router(items_router, prefix=API_V1_STR)
app.include_router(ai_router, prefix=API_V1_STR)
app.include_router(ai_plain_router, prefix=API_V1_STR)
app.include_router(rag_router, prefix=API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to the {PROJECT_NAME} API!",
        "documentation": "Visit /docs for the interactive Swagger API documentation."
    }
