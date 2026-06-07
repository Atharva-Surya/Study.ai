from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ==========================================
# USER BASE SCHEMA
# ==========================================
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid email address")

# ==========================================
# USER REGISTRATION SCHEMA
# ==========================================
# Used when registering a new user. Expects username, email, and password.
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="Password (min 6 characters)")

# ==========================================
# USER LOGIN SCHEMA
# ==========================================
# Used when authenticating a user.
class UserLogin(BaseModel):
    username: str
    password: str

# ==========================================
# USER RESPONSE SCHEMA
# ==========================================
# Formats the user profile data returned to the client.
# We do NOT return the hashed_password here!
class UserOut(UserBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

# ==========================================
# JWT TOKEN SCHEMAS
# ==========================================
# Formats the login response token.
class Token(BaseModel):
    access_token: str
    token_type: str

# Represents the data extracted from a verified JWT token.
class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
