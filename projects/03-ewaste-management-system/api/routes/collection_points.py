"""
Collection Points Routes
Manage and list collection centers
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from math import radians, sin, cos, sqrt, atan2

from utils.database import SessionLocal, CollectionPoint, User
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


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km."""
    R = 6371  # Earth's radius in km
    
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


@router.get("", response_model=list)
async def list_collection_points(
    token: str = Query(...),
    city: str = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    List collection points
    
    **Query Parameters:**
    - token: str (JWT)
    - city: str (optional)
    - active_only: bool (default True)
    
    **Response:**
    List of collection points
    """
    try:
        user = verify_token_and_get_user(token, db)
        
        query = db.query(CollectionPoint)
        
        if active_only:
            query = query.filter(CollectionPoint.status == "Active")
        
        if city:
            query = query.filter(CollectionPoint.city.ilike(f"%{city}%"))
        
        points = query.all()
        
        return [
            {
                "id": p.id,
                "name": p.name,
                "address": p.address,
                "city": p.city,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "capacity": p.capacity,
                "current_load": p.current_load,
                "phone": p.phone,
                "status": p.status,
                "utilization": round((p.current_load / p.capacity * 100), 2) if p.capacity > 0 else 0,
            }
            for p in points
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"List collection points error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve collection points"
        )


@router.get("/nearby", response_model=list)
async def get_nearby_points(
    token: str = Query(...),
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius_km: float = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Find nearby collection points
    
    **Query Parameters:**
    - token: str (JWT)
    - latitude: float (required)
    - longitude: float (required)
    - radius_km: float (1-100, default 10)
    
    **Response:**
    List of nearby collection points sorted by distance
    """
    try:
        user = verify_token_and_get_user(token, db)
        
        points = db.query(CollectionPoint).filter(
            CollectionPoint.status == "Active"
        ).all()
        
        nearby = []
        for point in points:
            distance = haversine_distance(
                latitude, longitude,
                point.latitude, point.longitude
            )
            
            if distance <= radius_km:
                nearby.append({
                    "id": point.id,
                    "name": point.name,
                    "address": point.address,
                    "city": point.city,
                    "latitude": point.latitude,
                    "longitude": point.longitude,
                    "phone": point.phone,
                    "distance_km": round(distance, 2),
                    "utilization": round((point.current_load / point.capacity * 100), 2) if point.capacity > 0 else 0,
                })
        
        # Sort by distance
        nearby.sort(key=lambda x: x["distance_km"])
        
        app_logger.info(f"Found {len(nearby)} nearby collection points for user {user.email}")
        
        return nearby
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Get nearby points error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve nearby points"
        )


@router.get("/{point_id}", response_model=dict)
async def get_collection_point(
    point_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get specific collection point details
    
    **Path Parameters:**
    - point_id: str
    
    **Query Parameters:**
    - token: str (JWT)
    
    **Response:**
    Collection point details
    """
    try:
        user = verify_token_and_get_user(token, db)
        
        point = db.query(CollectionPoint).filter(CollectionPoint.id == point_id).first()
        
        if not point:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection point not found"
            )
        
        return {
            "id": point.id,
            "name": point.name,
            "address": point.address,
            "city": point.city,
            "latitude": point.latitude,
            "longitude": point.longitude,
            "capacity": point.capacity,
            "current_load": point.current_load,
            "phone": point.phone,
            "status": point.status,
            "utilization": round((point.current_load / point.capacity * 100), 2) if point.capacity > 0 else 0,
            "created_at": point.created_at.isoformat(),
            "updated_at": point.updated_at.isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Get collection point error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve collection point"
        )
