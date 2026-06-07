"""
Pydantic models for data validation
"""
from pydantic import BaseModel, EmailStr, Field, validator, ValidationError
from typing import Optional, List
from datetime import datetime
import re

# ==================== USER MODELS ====================

class UserCreate(BaseModel):
    """User creation schema"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    address: str = Field(..., min_length=5, max_length=500)
    city: str = Field(default="Pune", max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    
    @validator("phone")
    def validate_phone(cls, v):
        # Accept Indian phone numbers
        if not re.match(r'^(\+91)?[6-9]\d{9}$', v.replace("-", "").replace(" ", "")):
            raise ValueError("Invalid phone number format")
        return v
    
    @validator("name")
    def validate_name(cls, v):
        if not v.replace(" ", "").isalpha():
            raise ValueError("Name should only contain letters and spaces")
        return v

class User(BaseModel):
    """User response model"""
    id: int
    name: str
    email: str
    phone: str
    address: str
    city: str
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== E-WASTE SUBMISSION MODELS ====================

class EWasteSubmissionCreate(BaseModel):
    """E-waste submission schema"""
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    email: EmailStr
    address: str = Field(..., min_length=5, max_length=500)
    item_type: str = Field(..., min_length=2, max_length=100)
    quantity: int = Field(..., gt=0, le=100)
    condition: str = Field(..., pattern="^(Working|Partially Working|Broken/Non-functional)$")
    collection_point: str = Field(..., max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator("phone")
    def validate_phone(cls, v):
        if not re.match(r'^(\+91)?[6-9]\d{9}$', v.replace("-", "").replace(" ", "")):
            raise ValueError("Invalid phone number format")
        return v
    
    @validator("item_type")
    def validate_item_type(cls, v):
        valid_types = [
            "Mobile Phone", "Laptop", "Desktop Computer", "Television",
            "Refrigerator", "Washing Machine", "Air Conditioner", 
            "Printer", "Battery", "Other"
        ]
        if v not in valid_types:
            raise ValueError(f"Invalid item type. Must be one of: {valid_types}")
        return v

class EWasteSubmission(EWasteSubmissionCreate):
    """E-waste submission response model"""
    id: str
    status: str
    priority: str
    hazard_level: str
    co2_saved: float
    weight_kg: float
    recycle_value: float
    date: datetime
    
    class Config:
        from_attributes = True

# ==================== COLLECTION POINT MODELS ====================

class CollectionPointCreate(BaseModel):
    """Collection point creation schema"""
    name: str = Field(..., min_length=2, max_length=100)
    address: str = Field(..., min_length=5, max_length=500)
    city: str = Field(default="Pune", max_length=50)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    capacity: int = Field(..., gt=0)
    phone: str = Field(..., min_length=10, max_length=15)
    
    @validator("phone")
    def validate_phone(cls, v):
        if not re.match(r'^(\+91)?[6-9]\d{9}$', v.replace("-", "").replace(" ", "")):
            raise ValueError("Invalid phone number format")
        return v

class CollectionPoint(CollectionPointCreate):
    """Collection point response model"""
    id: int
    status: str = "Active"
    current_load: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== LOGIN MODELS ====================

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)

class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours in seconds
    user_id: str
    email: str
    is_admin: bool

# ==================== FILTER MODELS ====================

class SubmissionFilter(BaseModel):
    """Submission filter schema"""
    status: Optional[str] = None
    priority: Optional[str] = None
    item_type: Optional[str] = None
    city: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)

# ==================== ERROR RESPONSE MODELS ====================

class ErrorResponse(BaseModel):
    """Standard error response"""
    code: str
    message: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ValidationErrorDetail(BaseModel):
    """Validation error detail"""
    field: str
    message: str
    value: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    code: str = "VALIDATION_ERROR"
    message: str = "Validation failed"
    errors: List[ValidationErrorDetail]
    timestamp: datetime = Field(default_factory=datetime.now)
