from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_model import User
from app.auth.security import SECRET_KEY, ALGORITHM
from app.schemas.user_schema import TokenData

# =====================================================================
# CONCEPT: OAUTH2 PASSWORD BEARER
# =====================================================================
# oauth2_scheme is a dependency provider. It instructs FastAPI to check
# the request headers for: "Authorization: Bearer <TOKEN>".
# If the header is missing, it automatically returns an HTTP 401 Unauthorized.
# tokenUrl specifies where the client should send username/password to get a token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to secure routes.
    It extracts the JWT token from the headers, verifies it,
    queries the user from the database, and injects the user object into the route.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the token using our secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract fields from the payload.
        # "sub" is a standard JWT claim representing the Subject of the token (we store username or id).
        # Let's extract the subject and user_id. We'll store user_id as sub or custom fields.
        # For our application, we will store the username as "sub" and user_id as "user_id".
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None or user_id is None:
            raise credentials_exception
            
        token_data = TokenData(username=username, user_id=user_id)
    except JWTError:
        # JWTError is raised if the token is expired, tampered with, or invalid
        raise credentials_exception

    # Query the database to fetch the actual User model
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
        
    return user
