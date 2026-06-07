"""
Analytics Routes
Dashboard statistics and insights
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from utils.database import SessionLocal, EWasteSubmission, User
from utils.logger import app_logger
from utils.auth import AuthService

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_token_and_get_user(token: str, db: Session) -> User:
    """Helper: Verify token and return user object."""
    try:
        payload = AuthService.verify_token(token)
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
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


@router.get("/dashboard", response_model=dict)
async def dashboard_stats(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics for current user
    
    **Query Parameters:**
    - token: str (JWT)
    
    **Response:**
    - total_submissions: int
    - total_co2_saved: float (kg)
    - total_items: int
    - high_priority: int
    - status_breakdown: dict
    """
    try:
        user = verify_token_and_get_user(token, db)
        
        submissions = db.query(EWasteSubmission).filter(
            EWasteSubmission.user_id == user.id
        ).all()
        
        total_submissions = len(submissions)
        total_co2_saved = sum(s.co2_saved or 0 for s in submissions)
        total_items = sum(s.quantity or 0 for s in submissions)
        high_priority = len([s for s in submissions if s.priority == "High"])
        
        # Status breakdown
        status_breakdown = {}
        for status in ["Pending", "Collected", "Recycled"]:
            count = len([s for s in submissions if s.status == status])
            status_breakdown[status] = count
        
        # Priority breakdown
        priority_breakdown = {}
        for priority in ["Low", "Medium", "High"]:
            count = len([s for s in submissions if s.priority == priority])
            priority_breakdown[priority] = count
        
        return {
            "total_submissions": total_submissions,
            "total_co2_saved": round(total_co2_saved, 2),
            "total_items": total_items,
            "high_priority": high_priority,
            "status_breakdown": status_breakdown,
            "priority_breakdown": priority_breakdown,
            "total_recycle_value": round(sum(s.recycle_value or 0 for s in submissions), 2),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Dashboard stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard stats"
        )


@router.get("/submissions-by-type", response_model=dict)
async def submissions_by_type(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get submission count by item type
    
    **Query Parameters:**
    - token: str (JWT)
    
    **Response:**
    - {item_type: count}
    """
    try:
        user = verify_token_and_get_user(token, db)
        
        submissions = db.query(EWasteSubmission).filter(
            EWasteSubmission.user_id == user.id
        ).all()
        
        type_breakdown = {}
        for submission in submissions:
            item_type = submission.item_type
            type_breakdown[item_type] = type_breakdown.get(item_type, 0) + 1
        
        return type_breakdown
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Submissions by type error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve type breakdown"
        )


@router.get("/monthly-trend", response_model=list)
async def monthly_trend(
    token: str = Query(...),
    months: int = Query(6, ge=1, le=12),
    db: Session = Depends(get_db)
):
    """
    Get submissions trend over past months
    
    **Query Parameters:**
    - token: str (JWT)
    - months: int (1-12, default 6)
    
    **Response:**
    List of months with submission counts
    """
    try:
        user = verify_token_and_get_user(token, db)
        
        submissions = db.query(EWasteSubmission).filter(
            EWasteSubmission.user_id == user.id
        ).all()
        
        # Group by month
        trend = {}
        for i in range(months):
            month_date = datetime.now() - timedelta(days=30*i)
            month_key = month_date.strftime("%Y-%m")
            trend[month_key] = 0
        
        for submission in submissions:
            month_key = submission.created_at.strftime("%Y-%m")
            if month_key in trend:
                trend[month_key] += 1
        
        return [
            {"month": month, "count": count}
            for month, count in sorted(trend.items(), reverse=True)
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Monthly trend error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve monthly trend"
        )


@router.get("/impact-summary", response_model=dict)
async def impact_summary(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get environmental impact summary
    
    **Query Parameters:**
    - token: str (JWT)
    
    **Response:**
    - co2_saved: float (kg)
    - weight_recycled: float (kg)
    - recycle_value: float (USD)
    - tree_equivalents: int
    """
    try:
        user = verify_token_and_get_user(token, db)
        
        submissions = db.query(EWasteSubmission).filter(
            EWasteSubmission.user_id == user.id
        ).all()
        
        total_co2 = sum(s.co2_saved or 0 for s in submissions)
        total_weight = sum(s.weight_kg or 0 for s in submissions)
        total_value = sum(s.recycle_value or 0 for s in submissions)
        
        # 1 tree absorbs ~21kg CO2/year = ~0.06kg CO2/day
        tree_equivalents = int(total_co2 / 21)
        
        return {
            "co2_saved_kg": round(total_co2, 2),
            "weight_recycled_kg": round(total_weight, 2),
            "recycle_value_usd": round(total_value, 2),
            "tree_equivalents": tree_equivalents,
            "submissions_count": len(submissions),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Impact summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve impact summary"
        )
