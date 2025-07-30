from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User, UserRole
from app.utils.security import get_password_hash

def create_admin_user():
    """
    Create admin user if it doesn't exist
    """
    db = next(get_db())
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            return admin_user
        
        # Create admin user
        hashed_password = get_password_hash("admin123")
        admin_user = User(
            username="admin",
            email="admin@istqb.com",
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        return admin_user
    finally:
        db.close()

def get_admin_stats():
    """
    Get user and role statistics for admin dashboard
    """
    db = next(get_db())
    try:
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        admin_users = db.query(User).filter(User.role == UserRole.ADMIN).count()
        regular_users = db.query(User).filter(User.role == UserRole.USER).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admin_users,
            "regular_users": regular_users
        }
    finally:
        db.close()