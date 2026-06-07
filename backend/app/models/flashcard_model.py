from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# ==========================================
# FLASHCARD DATABASE MODEL
# ==========================================
# This class defines the 'flashcards' table in our database.
# Flashcards are AI-generated question-and-answer pairs linked to a study item.
class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    
    # Foreign key linking this flashcard to a study item
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)

    # Relationship linking this flashcard back to its Item
    item = relationship("Item", back_populates="flashcards")
