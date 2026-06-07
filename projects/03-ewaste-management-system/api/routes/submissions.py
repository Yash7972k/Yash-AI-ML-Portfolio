"""
E-Waste Submissions Routes
Handles CRUD operations for e-waste submissions
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import uuid

from utils.database import SessionLocal, EWasteSubmission, User
from utils.models import EWasteSubmissionCreate
from utils.logger import app_logger
from utils.classifier import classify_item
from utils.impact import calculate_impact
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


@router.post("", status_code=201, response_model=dict)
async def create_submission(
    submission_data: EWasteSubmissionCreate,
    token: str = Query(..., description="JWT token"),
    db: Session = Depends(get_db)
):
    """
    Create a new e-waste submission
    
    **Request Body:**
    - name: str
    - phone: str (Indian format)
    - email: str
    - address: str
    - item_type: str (from allowed list)
    - quantity: int (1-100)
    - condition: str (Working/Partially Working/Broken/Non-functional)
    - notes: str (optional)
    
    **Query Parameters:**
    - token: str (JWT)
    
    **Response:**
    - id: str
    - status: str (Pending)
    - priority: str
    - hazard_level: str
    - co2_saved: float
    - recycling_tip: str
    """
    try:
        user = verify_token_and_get_user(token, db)
        
        # Classify e-waste
        classification = classify_item(submission_data.item_type, submission_data.quantity, submission_data.condition)
        
        # Calculate environmental impact
        impact = calculate_impact(submission_data.item_type, submission_data.quantity)
        
        # Create submission
        submission = EWasteSubmission(
            id=str(uuid.uuid4()),
            user_id=user.id,
            name=submission_data.name,
            phone=submission_data.phone,
            email=submission_data.email,
            address=submission_data.address,
            item_type=submission_data.item_type,
            quantity=submission_data.quantity,
            condition=submission_data.condition,
            collection_point=submission_data.collection_point,
            status="Pending",
            priority=classification["priority"],
            hazard_level=classification["hazard_level"],
            co2_saved=impact["co2_saved_kg"],
            weight_kg=impact["weight_kg"],
            recycle_value=impact["recycle_value_usd"],
            notes=submission_data.notes or "",
        )
        
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        app_logger.info(f"Submission created: {submission.id} by user {user.email}")
        
        return {
            "id": submission.id,
            "status": submission.status,
            "priority": submission.priority,
            "hazard_level": submission.hazard_level,
            "co2_saved": submission.co2_saved,
            "recycling_tip": classification["recycling_tip"],
            "created_at": submission.created_at.isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        app_logger.error(f"Submission creation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create submission"
        )


@router.get("", response_model=list)
async def list_submissions(
    token: str = Query(...),
    status_filter: str = Query(None, alias="status"),
    priority_filter: str = Query(None, alias="priority"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List e-waste submissions with filtering
    
    **Query Parameters:**
    - token: str (JWT)
    - status: str (optional - Pending/Collected/Recycled)
    - priority: str (optional - Low/Medium/High)
    - limit: int (1-1000, default 100)
    - offset: int (pagination, default 0)
    
    **Response:**
    List of submissions with pagination
    """
    try:
        user = verify_token_and_get_user(token, db)
        
        # Build query
        query = db.query(EWasteSubmission).filter(EWasteSubmission.user_id == user.id)
        
        if status_filter:
            query = query.filter(EWasteSubmission.status == status_filter)
        
        if priority_filter:
            query = query.filter(EWasteSubmission.priority == priority_filter)
        
        # Order by date descending
        query = query.order_by(desc(EWasteSubmission.created_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        submissions = query.limit(limit).offset(offset).all()
        
        app_logger.info(f"User {user.email} retrieved {len(submissions)} submissions")
        
        return [
            {
                "id": s.id,
                "item_type": s.item_type,
                "quantity": s.quantity,
                "status": s.status,
                "priority": s.priority,
                "co2_saved": s.co2_saved,
                "created_at": s.created_at.isoformat(),
            }
            for s in submissions
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"List submissions error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve submissions"
        )


@router.get("/{submission_id}", response_model=dict)
async def get_submission(
    submission_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get specific submission details
    
    **Path Parameters:**
    - submission_id: str (UUID)
    
    **Query Parameters:**
    - token: str (JWT)
    
    **Response:**
    Complete submission details
    """
    try:
        user = verify_token_and_get_user(token, db)
        
        submission = db.query(EWasteSubmission).filter(
            EWasteSubmission.id == submission_id,
            EWasteSubmission.user_id == user.id
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        return {
            "id": submission.id,
            "name": submission.name,
            "phone": submission.phone,
            "email": submission.email,
            "address": submission.address,
            "item_type": submission.item_type,
            "quantity": submission.quantity,
            "condition": submission.condition,
            "status": submission.status,
            "priority": submission.priority,
            "hazard_level": submission.hazard_level,
            "co2_saved": submission.co2_saved,
            "weight_kg": submission.weight_kg,
            "recycle_value": submission.recycle_value,
            "notes": submission.notes,
            "created_at": submission.created_at.isoformat(),
            "updated_at": submission.updated_at.isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Get submission error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve submission"
        )


@router.patch("/{submission_id}", response_model=dict)
async def update_submission(
    submission_id: str,
    updates: dict,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Update submission status/notes
    
    **Path Parameters:**
    - submission_id: str
    
    **Request Body:**
    - status: str (optional)
    - notes: str (optional)
    
    **Query Parameters:**
    - token: str (JWT)
    """
    try:
        user = verify_token_and_get_user(token, db)
        
        submission = db.query(EWasteSubmission).filter(
            EWasteSubmission.id == submission_id,
            EWasteSubmission.user_id == user.id
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        # Update allowed fields
        if "status" in updates:
            submission.status = updates["status"]
        if "notes" in updates:
            submission.notes = updates["notes"]
        
        db.commit()
        db.refresh(submission)
        
        app_logger.info(f"Submission updated: {submission.id}")
        
        return {
            "id": submission.id,
            "status": submission.status,
            "updated_at": submission.updated_at.isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        app_logger.error(f"Update submission error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update submission"
        )


@router.delete("/{submission_id}", status_code=204)
async def delete_submission(
    submission_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Delete a submission (soft delete)
    
    **Path Parameters:**
    - submission_id: str
    
    **Query Parameters:**
    - token: str (JWT)
    """
    try:
        user = verify_token_and_get_user(token, db)
        
        submission = db.query(EWasteSubmission).filter(
            EWasteSubmission.id == submission_id,
            EWasteSubmission.user_id == user.id
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        db.delete(submission)
        db.commit()
        
        app_logger.info(f"Submission deleted: {submission_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        app_logger.error(f"Delete submission error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete submission"
        )
