from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.schemas.ai_schema import (
    ChatRequest,
    ChatResponse,
    FlashcardRequest,
    FlashcardItem,
    QuizRequest,
    QuizQuestionItem,
    FlashcardResponse,
    QuizQuestionResponse,
)
from app.services.ai_service import AIService
from app.auth.dependencies import get_current_user
from app.cache import get_cache_key, get_cached, set_cached, invalidate_user_cache

router = APIRouter(prefix="/ai", tags=["AI Study Assistant"])
plain_router = APIRouter(prefix="", tags=["AI Study Assistant"])

@plain_router.post("/chat", response_model=ChatResponse, summary="Chat with the AI assistant")
async def chat_alias(
    request: ChatRequest,
    req: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Alias endpoint for frontend clients calling /api/v1/chat.
    """
    redis = req.app.state.redis if hasattr(req.app.state, "redis") else None
    import json
    cache_key = await get_cache_key("chat", current_user.id, json.dumps([m.dict() if hasattr(m, "dict") else m for m in request.messages]))
    cached_reply = await get_cached(redis, cache_key)
    if cached_reply:
        return ChatResponse(reply=cached_reply)
    answer = await AIService.chat(request.messages)
    await set_cached(redis, cache_key, answer, ttl=900)
    return ChatResponse(reply=answer)

@plain_router.post("/generate-flashcards", response_model=List[FlashcardItem], summary="Generate flashcards from a topic")
async def generate_flashcards_topic(
    request: FlashcardRequest,
    req: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create concise study flashcards from a topic or description.
    """
    try:
        redis = req.app.state.redis if hasattr(req.app.state, "redis") else None
        cache_key = await get_cache_key("fc_topic", current_user.id, f"{request.topic}:{request.details}")
        cached_cards = await get_cached(redis, cache_key)
        if cached_cards:
            return cached_cards
        cards = await AIService.generate_flashcards_for_topic(request.topic, request.details)
        await set_cached(redis, cache_key, cards, ttl=7200)
        return cards
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate flashcards: {str(e)}"
        )

@plain_router.post("/generate-quiz", response_model=List[QuizQuestionItem], summary="Generate a quiz from a topic")
async def generate_quiz_topic(
    request: QuizRequest,
    req: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create multiple-choice quiz questions from a topic or description.
    """
    try:
        redis = req.app.state.redis if hasattr(req.app.state, "redis") else None
        cache_key = await get_cache_key("quiz_topic", current_user.id, f"{request.topic}:{request.details}")
        cached_questions = await get_cached(redis, cache_key)
        if cached_questions:
            return cached_questions
        questions = await AIService.generate_quiz_for_topic(request.topic, request.details)
        await set_cached(redis, cache_key, questions, ttl=7200)
        return questions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quiz: {str(e)}"
        )

# =====================================================================
# 1. RETRIEVE FLASHCARDS (GET)
# =====================================================================
@router.get("/flashcards/{item_id}", response_model=List[FlashcardResponse], summary="Retrieve existing AI flashcards for a study item")
async def get_flashcards(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all pre-generated flashcards for a specific study topic.
    """
    redis = request.app.state.redis if hasattr(request.app.state, "redis") else None
    cache_key = await get_cache_key("flashcards", current_user.id, str(item_id))
    cached_cards = await get_cached(redis, cache_key)
    if cached_cards:
        return cached_cards
    cards = await AIService.get_flashcards(db, item_id, current_user.id)
    await set_cached(redis, cache_key, cards)
    return cards

# =====================================================================
# 2. GENERATE FLASHCARDS (POST)
# =====================================================================
@router.post("/generate-flashcards/{item_id}", response_model=List[FlashcardResponse], summary="Generate and save flashcards for a study item")
async def generate_flashcards(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate new flashcards for a study topic.
    This overwrites any previously generated flashcards for this topic.
    """
    try:
        cards = await AIService.generate_flashcards(db, item_id, current_user.id)
        redis = request.app.state.redis if hasattr(request.app.state, "redis") else None
        cache_key = await get_cache_key("flashcards", current_user.id, str(item_id))
        await set_cached(redis, cache_key, cards)
        return cards
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating flashcards: {str(e)}"
        )

# =====================================================================
# 3. RETRIEVE QUIZ QUESTIONS (GET)
# =====================================================================
@router.get("/quiz/{item_id}", response_model=List[QuizQuestionResponse], summary="Retrieve existing AI quiz questions for a study item")
async def get_quiz(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all pre-generated multiple choice quiz questions for a specific study topic.
    """
    redis = request.app.state.redis if hasattr(request.app.state, "redis") else None
    cache_key = await get_cache_key("quiz", current_user.id, str(item_id))
    cached_questions = await get_cached(redis, cache_key)
    if cached_questions:
        return cached_questions
    questions = await AIService.get_quiz(db, item_id, current_user.id)
    await set_cached(redis, cache_key, questions)
    return questions

# =====================================================================
# 4. GENERATE QUIZ (POST)
# =====================================================================
@router.post("/chat", response_model=ChatResponse, summary="Chat with the AI assistant")
async def chat(
    request: ChatRequest,
    req: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a chat conversation to the AI assistant and receive a reply.
    """
    redis = req.app.state.redis if hasattr(req.app.state, "redis") else None
    import json
    cache_key = await get_cache_key("chat", current_user.id, json.dumps([m.dict() if hasattr(m, "dict") else m for m in request.messages]))
    cached_reply = await get_cached(redis, cache_key)
    if cached_reply:
        return ChatResponse(reply=cached_reply)
    answer = await AIService.chat(request.messages)
    await set_cached(redis, cache_key, answer, ttl=900)
    return ChatResponse(reply=answer)


@router.post("/generate-quiz/{item_id}", response_model=List[QuizQuestionResponse], summary="Generate and save a quiz for a study item")
async def generate_quiz(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a new multiple-choice quiz for a study topic.
    This overwrites any previously generated quiz questions for this topic.
    """
    try:
        questions = await AIService.generate_quiz(db, item_id, current_user.id)
        redis = request.app.state.redis if hasattr(request.app.state, "redis") else None
        cache_key = await get_cache_key("quiz", current_user.id, str(item_id))
        await set_cached(redis, cache_key, questions)
        return questions
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating the quiz: {str(e)}"
        )
