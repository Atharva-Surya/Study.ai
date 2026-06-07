from pydantic import BaseModel, Field, field_validator
from typing import List, Union, Optional
import json

# ==========================================
# CHAT SCHEMAS
# ==========================================
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    reply: str


class FlashcardRequest(BaseModel):
    topic: str
    details: Optional[str] = ''


class QuizRequest(BaseModel):
    topic: str
    details: Optional[str] = ''


class FlashcardItem(BaseModel):
    question: str
    answer: str


class QuizQuestionItem(BaseModel):
    question: str
    options: List[str]
    correct_answer: str


# ==========================================
# FLASHCARD SCHEMAS
# ==========================================
class FlashcardResponse(BaseModel):
    id: int
    question: str
    answer: str
    item_id: int

    model_config = {
        "from_attributes": True
    }

class FlashcardGenerationResponse(BaseModel):
    flashcards: List[FlashcardResponse]


# ==========================================
# QUIZ SCHEMAS
# ==========================================
class QuizQuestionResponse(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_answer: str
    item_id: int

    model_config = {
        "from_attributes": True
    }

    # Custom validator to deserialize database string options into a list
    @field_validator("options", mode="before")
    @classmethod
    def parse_options(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
            # Fallback split if stored as semicolon-delimited string
            return [opt.strip() for opt in v.split(";") if opt.strip()]
        return v

class QuizGenerationResponse(BaseModel):
    quiz_questions: List[QuizQuestionResponse]
