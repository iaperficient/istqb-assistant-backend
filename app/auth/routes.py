from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, Token, UserInfo
from app.auth.oauth2 import get_current_active_user
from app.auth.role_middleware import require_admin_checker
from app.auth.admin_setup import get_admin_stats
from app.utils.security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(
            (User.email == user.email) | (User.username == user.username)
        ).first()
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Email or username already registered"
            )
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            role=user.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Error in register_user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
    }

@router.get("/me", response_model=UserInfo)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information including role"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value,
        "is_admin": current_user.is_admin,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }

@router.put("/users/{user_id}/deactivate")
def deactivate_user(user_id: int, db: Session = Depends(get_db), admin_user: User = Depends(require_admin_checker)):
    """Deactivate a user (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    if user.is_admin:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate admin users"
        )
    
    user.is_active = False
    db.commit()
    db.refresh(user)
    
    return {
        "status": "success",
        "message": f"User {user.username} has been deactivated",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
    }

@router.get("/admin/stats")
def get_user_stats(admin_user: User = Depends(require_admin_checker)):
    """Get user and role statistics (Admin only)"""
    stats = get_admin_stats()
    return {
        "status": "success",
        "data": stats,
        "requested_by": {
            "username": admin_user.username,
            "role": admin_user.role.value
        }
    }