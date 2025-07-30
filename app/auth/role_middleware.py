from fastapi import Depends, HTTPException, status
from app.auth.oauth2 import get_current_active_user
from app.models.user import User, UserRole

def require_admin_checker(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to check if the current user has admin privileges
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user

def require_role(required_role: UserRole):
    """
    Dependency factory to check if user has the required role
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. {required_role.value} role required."
            )
        return current_user
    return role_checker