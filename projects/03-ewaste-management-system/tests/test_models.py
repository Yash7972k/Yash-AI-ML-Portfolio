"""
Unit Tests for Validation Models
Tests Pydantic models for input validation
"""

import pytest
from pydantic import ValidationError
from utils.models import (
    UserCreate, LoginRequest, EWasteSubmissionCreate,
    CollectionPointCreate, SubmissionFilter
)


class TestUserCreate:
    """Test UserCreate validation model"""
    
    def test_user_create_valid(self):
        """Test valid user creation"""
        user = UserCreate(
            name="John Doe",
            email="john@example.com",
            phone="+919876543210",
            address="123 Main St",
            password="StrongPass123!"
        )
        
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.phone == "+919876543210"
    
    def test_user_create_invalid_email(self):
        """Test invalid email"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                name="John Doe",
                email="invalid_email",
                phone="+919876543210",
                address="123 Main St",
                password="StrongPass123!"
            )
        assert "email" in str(exc_info.value).lower()
    
    def test_user_create_invalid_phone(self):
        """Test invalid Indian phone number"""
        with pytest.raises(ValidationError):
            UserCreate(
                name="John Doe",
                email="john@example.com",
                phone="123",  # Invalid format
                address="123 Main St",
                password="StrongPass123!"
            )
    
    def test_user_create_name_too_short(self):
        """Test name too short"""
        with pytest.raises(ValidationError):
            UserCreate(
                name="A",  # Too short
                email="john@example.com",
                phone="+919876543210",
                address="123 Main St",
                password="StrongPass123!"
            )
    
    def test_user_create_password_too_short(self):
        """Test password too short"""
        with pytest.raises(ValidationError):
            UserCreate(
                name="John Doe",
                email="john@example.com",
                phone="+919876543210",
                address="123 Main St",
                password="short"  # Too short
            )


class TestLoginRequest:
    """Test LoginRequest model"""
    
    def test_login_request_valid(self):
        """Test valid login request"""
        login = LoginRequest(
            email="john@example.com",
            password="TestPass123!"
        )
        
        assert login.email == "john@example.com"
        assert login.password == "TestPass123!"
    
    def test_login_request_invalid_email(self):
        """Test invalid email in login"""
        with pytest.raises(ValidationError):
            LoginRequest(
                email="not_an_email",
                password="TestPass123!"
            )


class TestEWasteSubmissionCreate:
    """Test EWasteSubmissionCreate model"""
    
    def test_submission_valid(self):
        """Test valid submission"""
        submission = EWasteSubmissionCreate(
            name="John Doe",
            phone="+919876543210",
            email="john@example.com",
            address="123 Main St",
            item_type="Mobile Phone",
            quantity=5,
            condition="Working",
            notes="In good condition"
        )
        
        assert submission.item_type == "Mobile Phone"
        assert submission.quantity == 5
        assert submission.condition == "Working"
    
    def test_submission_invalid_item_type(self):
        """Test invalid item type"""
        with pytest.raises(ValidationError):
            EWasteSubmissionCreate(
                name="John Doe",
                phone="+919876543210",
                email="john@example.com",
                address="123 Main St",
                item_type="Invalid Item",  # Not in allowed list
                quantity=5,
                condition="Working"
            )
    
    def test_submission_quantity_too_high(self):
        """Test quantity exceeds limit"""
        with pytest.raises(ValidationError):
            EWasteSubmissionCreate(
                name="John Doe",
                phone="+919876543210",
                email="john@example.com",
                address="123 Main St",
                item_type="Mobile Phone",
                quantity=101,  # Max is 100
                condition="Working"
            )
    
    def test_submission_quantity_too_low(self):
        """Test quantity below minimum"""
        with pytest.raises(ValidationError):
            EWasteSubmissionCreate(
                name="John Doe",
                phone="+919876543210",
                email="john@example.com",
                address="123 Main St",
                item_type="Mobile Phone",
                quantity=0,  # Min is 1
                condition="Working"
            )
    
    def test_submission_invalid_condition(self):
        """Test invalid condition"""
        with pytest.raises(ValidationError):
            EWasteSubmissionCreate(
                name="John Doe",
                phone="+919876543210",
                email="john@example.com",
                address="123 Main St",
                item_type="Mobile Phone",
                quantity=5,
                condition="Invalid Condition"
            )
    
    def test_submission_invalid_phone(self):
        """Test invalid phone in submission"""
        with pytest.raises(ValidationError):
            EWasteSubmissionCreate(
                name="John Doe",
                phone="12345",  # Invalid format
                email="john@example.com",
                address="123 Main St",
                item_type="Mobile Phone",
                quantity=5,
                condition="Working"
            )


class TestSubmissionFilter:
    """Test SubmissionFilter model"""
    
    def test_filter_valid(self):
        """Test valid filter"""
        filter_obj = SubmissionFilter(
            limit=50,
            offset=0
        )
        
        assert filter_obj.limit == 50
        assert filter_obj.offset == 0
    
    def test_filter_default_values(self):
        """Test filter default values"""
        filter_obj = SubmissionFilter()
        
        assert filter_obj.limit == 100
        assert filter_obj.offset == 0
    
    def test_filter_invalid_limit(self):
        """Test invalid limit (too high)"""
        with pytest.raises(ValidationError):
            SubmissionFilter(
                limit=10001,  # Max is 10000
                offset=0
            )
