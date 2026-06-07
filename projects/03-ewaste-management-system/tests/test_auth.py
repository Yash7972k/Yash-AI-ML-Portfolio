"""
Unit Tests for Authentication Module
Tests JWT token creation, password hashing, token verification
"""

import pytest
from datetime import timedelta
from utils.auth import AuthService
from utils.models import TokenResponse


class TestAuthService:
    """Test AuthService class"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "TestPassword123!"
        hashed = AuthService.hash_password(password)
        
        # Hash should not be empty
        assert hashed is not None
        assert len(hashed) > 0
        
        # Hash should not be the same as password
        assert hashed != password
        
        # Hashes should be different for same password (salt)
        hashed2 = AuthService.hash_password(password)
        assert hashed != hashed2
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "TestPassword123!"
        hashed = AuthService.hash_password(password)
        
        # Verification should pass
        assert AuthService.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = AuthService.hash_password(password)
        
        # Verification should fail
        assert AuthService.verify_password(wrong_password, hashed) is False
    
    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = AuthService.create_access_token(data, expires_delta=timedelta(hours=1))
        
        # Token should not be empty
        assert token is not None
        assert len(token) > 0
        
        # Token should be a string
        assert isinstance(token, str)
        
        # Token should have JWT structure (3 parts separated by dots)
        parts = token.split(".")
        assert len(parts) == 3
    
    def test_verify_token_valid(self):
        """Test token verification with valid token"""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = AuthService.create_access_token(data, expires_delta=timedelta(hours=1))
        
        # Token verification should pass
        payload = AuthService.verify_token(token)
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == "123"
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token"""
        invalid_token = "invalid.token.here"
        
        # Token verification should fail
        with pytest.raises(Exception):
            AuthService.verify_token(invalid_token)
    
    def test_verify_token_expired(self):
        """Test token verification with expired token"""
        data = {"sub": "test@example.com", "user_id": "123"}
        # Create token that expires immediately
        token = AuthService.create_access_token(data, expires_delta=timedelta(seconds=0))
        
        # Wait a moment for token to expire
        import time
        time.sleep(0.1)
        
        # Token verification should fail
        with pytest.raises(Exception):
            AuthService.verify_token(token)


class TestTokenResponse:
    """Test TokenResponse model"""
    
    def test_token_response_valid(self):
        """Test TokenResponse creation"""
        response = TokenResponse(
            access_token="test_token",
            token_type="bearer",
            user_id="123",
            email="test@example.com",
            is_admin=False
        )
        
        assert response.access_token == "test_token"
        assert response.token_type == "bearer"
        assert response.user_id == "123"
        assert response.email == "test@example.com"
        assert response.is_admin is False
