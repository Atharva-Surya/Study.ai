from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# ==========================================
# USER DATABASE MODEL
# ==========================================
# This class defines the 'users' table in our database.
# Each attribute represents a column in the table.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship linking users to their study items
    # back_populates ensures changes on one side are synced to the other
    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
