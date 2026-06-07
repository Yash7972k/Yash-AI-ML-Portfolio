"""
Authentication Routes
Handles user login, registration, and token management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from datetime import timedelta

from utils.database import SessionLocal, User
from utils.auth import AuthService
from utils.models import LoginRequest, UserCreate, TokenResponse
from utils.logger import auth_logger
from utils.rate_limiting import RateLimits

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=dict, status_code=201)
@limiter.limit(RateLimits.AUTH_REGISTER)
async def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    **Request Body:**
    - name: str (2-100 characters)
    - email: str (valid email format)
    - phone: str (Indian format +91XXXXXXXXXX)
    - address: str (optional)
    - password: str (6+ characters)
    
    **Response:**
    - id: str
    - email: str
    - name: str
    - message: str
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            auth_logger.warning(f"Registration attempt with existing email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = AuthService.hash_password(user_data.password)
        
        # Create new user
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            address=user_data.address,
            city=user_data.city,
            password_hash=password_hash,
            is_active=True,
            is_admin=False,
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        auth_logger.info(f"New user registered: {user_data.email}")
        
        return {
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name,
            "message": "Registration successful"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        auth_logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
@limiter.limit(RateLimits.AUTH_LOGIN)
async def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    User login
    
    **Request Body:**
    - email: str
    - password: str
    
    **Response:**
    - access_token: str (JWT)
    - token_type: str (Bearer)
    - user_id: str
    - email: str
    - is_admin: bool
    """
    try:
        # Find user
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user:
            auth_logger.warning(f"Login attempt with non-existent email: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not AuthService.verify_password(credentials.password, user.password_hash):
            auth_logger.warning(f"Failed login attempt for: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            auth_logger.warning(f"Login attempt for inactive user: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Create JWT token
        access_token = AuthService.create_access_token(
            data={"sub": user.email, "user_id": str(user.id), "is_admin": user.is_admin},
            expires_delta=timedelta(hours=24)
        )
        
        auth_logger.info(f"User logged in: {credentials.email}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=86400,  # 24 hours in seconds
            user_id=str(user.id),
            email=user.email,
            is_admin=user.is_admin,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/verify-token")
async def verify_token(token: str):
    """
    Verify JWT token validity
    
    **Query Parameters:**
    - token: str (JWT token)
    
    **Response:**
    - valid: bool
    - email: str (if valid)
    - user_id: str (if valid)
    - error: str (if invalid)
    """
    try:
        payload = AuthService.verify_token(token)
        return {
            "valid": True,
            "email": payload.get("sub"),
            "user_id": payload.get("user_id"),
        }
    except Exception as e:
        auth_logger.warning(f"Token verification failed: {e}")
        return {
            "valid": False,
            "error": str(e),
        }


@router.get("/me")
async def get_current_user(token: str, db: Session = Depends(get_db)):
    """
    Get current logged-in user details
    
    **Query Parameters:**
    - token: str (JWT token)
    
    **Response:**
    - id: str
    - email: str
    - name: str
    - phone: str
    - is_admin: bool
    """
    try:
        payload = AuthService.verify_token(token)
        email = payload.get("sub")
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "is_admin": user.is_admin,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
