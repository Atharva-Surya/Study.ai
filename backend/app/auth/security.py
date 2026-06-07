import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# CONCEPT: CONFIGURATION & SECRETS
# ==========================================
# SECRET_KEY is used to cryptographically sign our JWT tokens.
# In production, this MUST be a long random string kept secret in .env.
# If not set, we provide a fallback for local development safety.
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret_study_assistant_key_change_me_in_production_1234567890")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


# ==========================================
# CONCEPT: PASSWORD HASHING CONTROLLER
# ==========================================
# We initialize the passlib context to use 'pbkdf2_sha256' first.
# This avoids bcrypt backend compatibility issues on some Python installs.
# The context can still verify bcrypt hashes if they already exist.
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password using the bcrypt algorithm. Used during User Registration."""
    return pwd_context.hash(password)
    """Hash a plain-text password using the bcrypt algorithm. Used during User Registration."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if a plain-text password matches the stored hash.
    Used during User Login.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ==========================================
# CONCEPT: JWT ACCESS TOKEN CREATION
# ==========================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a signed JSON Web Token (JWT).
    The 'data' dict represents the payload (claims) that we store in the token.
    We append an expiration date ('exp') so the token automatically expires.
    """
    to_encode = data.copy()
    
    # Calculate token expiration timestamp
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # "exp" is a standard JWT claim specifying expiration time
    to_encode.update({"exp": expire})
    
    # Encode and sign the JWT payload using our secret key and algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
