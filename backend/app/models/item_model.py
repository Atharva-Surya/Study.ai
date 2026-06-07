from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# ==========================================
# ITEM DATABASE MODEL
# ==========================================
# This class defines the 'items' table in our database.
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    
    # Foreign key linking this item to a specific user
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship linking this item back to its User owner
    owner = relationship("User", back_populates="items")

    # Relationships to AI-generated flashcards and quizzes
    flashcards = relationship("Flashcard", back_populates="item", cascade="all, delete-orphan")
    quiz_questions = relationship("QuizQuestion", back_populates="item", cascade="all, delete-orphan")

