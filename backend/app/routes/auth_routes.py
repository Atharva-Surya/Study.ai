from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserOut, Token
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ==========================================
# 1. USER REGISTRATION (POST)
# ==========================================
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED, summary="Register a new user")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    Hashes password and stores username, email, and password hash in the database.
    """
    # Check if a user with the same email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
        
    # Check if a user with the same username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken"
        )

    # Hash the password for security before saving it!
    hashed_pwd = hash_password(user_data.password)
    
    # Create the user instance
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd
    )
    
    db.add(new_user)
    db.commit()      # Save changes to the database
    db.refresh(new_user) # Load generated fields (like ID and created_at) from the DB
    
    return new_user

# ==========================================
# 2. USER LOGIN (POST)
# ==========================================
# We use OAuth2PasswordRequestForm which parses incoming requests submitted as form-data.
# This makes it compatible with Swagger UI's "Authorize" lock icon functionality.
@router.post("/login", response_model=Token, summary="Authenticate user and retrieve token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Log in and obtain a JWT access token.
    Accepts form parameters: username (which can be username or email) and password.
    """
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # If not found by username, let's try finding by email as a user convenience!
    if not user:
        user = db.query(User).filter(User.email == form_data.username).first()

    # If user doesn't exist or password verify fails, raise 401 Unauthorized
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate the access token
    # We embed the username as 'sub' and user_id in the token payload
    token_data = {"sub": user.username, "user_id": user.id}
    access_token = create_access_token(data=token_data)
    
    # Return the token payload complying with standard Bearer format
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# ==========================================
# 3. GET CURRENT PROFILE (GET)
# ==========================================
# This route is protected: it depends on get_current_user.
# If the caller doesn't provide a valid JWT token, they will get a 401.
@router.get("/me", response_model=UserOut, summary="Retrieve current logged-in user profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get profile details of the current logged-in user.
    Requires a valid JWT Bearer token in the Authorization header.
    """
    return current_user
