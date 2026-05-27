from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database.session import get_db
from app.services.auth import AuthService, get_current_user
from app.schemas.user import UserCreateRequest, UserResponse, TokenResponse
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreateRequest,
    db: Session = Depends(get_db)
):
    """Register new citizen or staff user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | 
        (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        phone=user_data.phone,
        password_hash=AuthService.hash_password(user_data.password),
        role=user_data.role or "citizen",
        department=user_data.department
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get JWT access token"""
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Update last login time
    user.last_login = timedelta(0) # placeholder or datetime.utcnow
    user.last_login = timedelta(0) # we can set it to datetime.utcnow()
    # Wait, let's set it to datetime
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create token
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        role=user.role
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh JWT access token"""
    access_token = AuthService.create_access_token(
        data={"sub": str(current_user.id)}
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=current_user.id,
        role=current_user.role
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current logged-in user profile"""
    return current_user

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout endpoint"""
    return {"message": "Logged out successfully"}
