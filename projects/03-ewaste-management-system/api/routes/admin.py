"""
Admin Routes
Admin-only operations and user management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from utils.database import SessionLocal, User, EWasteSubmission, CollectionPoint
from utils.logger import app_logger
from utils.auth import AuthService

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_token_and_get_admin(token: str, db: Session) -> User:
    """Helper: Verify token and ensure user is admin."""
    try:
        payload = AuthService.verify_token(token)
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.is_admin:
            app_logger.warning(f"Non-admin user {user.email} attempted admin access")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


@router.get("/stats", response_model=dict)
async def admin_stats(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get system-wide statistics (admin only)
    
    **Query Parameters:**
    - token: str (JWT)
    
    **Response:**
    - total_users: int
    - total_submissions: int
    - total_collection_points: int
    - total_co2_saved: float
    - status_breakdown: dict
    """
    try:
        admin = verify_token_and_get_admin(token, db)
        
        total_users = db.query(User).count()
        total_submissions = db.query(EWasteSubmission).count()
        total_points = db.query(CollectionPoint).count()
        
        submissions = db.query(EWasteSubmission).all()
        total_co2 = sum(s.co2_saved or 0 for s in submissions)
        
        # Status breakdown
        status_breakdown = {}
        for status in ["Pending", "Collected", "Recycled"]:
            count = db.query(EWasteSubmission).filter(
                EWasteSubmission.status == status
            ).count()
            status_breakdown[status] = count
        
        app_logger.info(f"Admin {admin.email} retrieved system stats")
        
        return {
            "total_users": total_users,
            "total_submissions": total_submissions,
            "total_collection_points": total_points,
            "total_co2_saved": round(total_co2, 2),
            "status_breakdown": status_breakdown,
            "total_recycle_value": round(sum(s.recycle_value or 0 for s in submissions), 2),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Admin stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve admin stats"
        )


@router.get("/users", response_model=list)
async def list_all_users(
    token: str = Query(...),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all users (admin only)
    
    **Query Parameters:**
    - token: str (JWT)
    - limit: int (default 100)
    - offset: int (pagination, default 0)
    
    **Response:**
    List of users
    """
    try:
        admin = verify_token_and_get_admin(token, db)
        
        users = db.query(User).limit(limit).offset(offset).all()
        
        return [
            {
                "id": u.id,
                "email": u.email,
                "name": u.name,
                "phone": u.phone,
                "is_admin": u.is_admin,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"List users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.patch("/users/{user_id}", response_model=dict)
async def update_user(
    user_id: str,
    updates: dict,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Update user status/role (admin only)
    
    **Path Parameters:**
    - user_id: str
    
    **Request Body:**
    - is_active: bool (optional)
    - is_admin: bool (optional)
    
    **Query Parameters:**
    - token: str (JWT)
    """
    try:
        admin = verify_token_and_get_admin(token, db)
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if "is_active" in updates:
            user.is_active = updates["is_active"]
        if "is_admin" in updates:
            user.is_admin = updates["is_admin"]
        
        db.commit()
        db.refresh(user)
        
        app_logger.info(f"Admin {admin.email} updated user {user_id}")
        
        return {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        app_logger.error(f"Update user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.get("/submissions", response_model=list)
async def list_all_submissions(
    token: str = Query(...),
    status_filter: str = Query(None, alias="status"),
    priority_filter: str = Query(None, alias="priority"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all submissions (admin only)
    
    **Query Parameters:**
    - token: str (JWT)
    - status: str (optional)
    - priority: str (optional)
    - limit: int (default 100)
    - offset: int (pagination, default 0)
    """
    try:
        admin = verify_token_and_get_admin(token, db)
        
        query = db.query(EWasteSubmission)
        
        if status_filter:
            query = query.filter(EWasteSubmission.status == status_filter)
        
        if priority_filter:
            query = query.filter(EWasteSubmission.priority == priority_filter)
        
        submissions = query.limit(limit).offset(offset).all()
        
        return [
            {
                "id": s.id,
                "user_id": s.user_id,
                "item_type": s.item_type,
                "quantity": s.quantity,
                "status": s.status,
                "priority": s.priority,
                "hazard_level": s.hazard_level,
                "co2_saved": s.co2_saved,
                "created_at": s.created_at.isoformat(),
            }
            for s in submissions
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"List all submissions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve submissions"
        )


@router.patch("/submissions/{submission_id}", response_model=dict)
async def update_submission_status(
    submission_id: str,
    updates: dict,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Update submission status (admin only)
    
    **Path Parameters:**
    - submission_id: str
    
    **Request Body:**
    - status: str (Pending/Collected/Recycled)
    - priority: str (optional)
    
    **Query Parameters:**
    - token: str (JWT)
    """
    try:
        admin = verify_token_and_get_admin(token, db)
        
        submission = db.query(EWasteSubmission).filter(
            EWasteSubmission.id == submission_id
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        if "status" in updates:
            submission.status = updates["status"]
        if "priority" in updates:
            submission.priority = updates["priority"]
        
        db.commit()
        db.refresh(submission)
        
        app_logger.info(f"Admin {admin.email} updated submission {submission_id}")
        
        return {
            "id": submission.id,
            "status": submission.status,
            "priority": submission.priority,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        app_logger.error(f"Update submission status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update submission"
        )
