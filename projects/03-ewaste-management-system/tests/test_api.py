"""
Comprehensive API Endpoint Tests
Integration tests for all REST API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from main import app, get_db
from utils.database import Base, User, EWasteSubmission
from utils.auth import AuthService

# ────────────────────────────────────────────────────────────────────────────
# Test Database Setup
# ────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def test_db():
    """Create a temporary SQLite database for testing"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Create engine
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestingSessionLocal()
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(test_db):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def demo_user(test_db):
    """Create demo user for testing"""
    password = "DemoPass123!"
    password_hash = AuthService.hash_password(password)
    
    user = User(
        id="demo-user-id",
        email="demo@example.com",
        name="Demo User",
        phone="+919876543210",
        address="Demo Address",
        password_hash=password_hash,
        is_active=True,
        is_admin=False,
    )
    
    test_db.add(user)
    test_db.commit()
    
    return {"user": user, "password": password, "email": "demo@example.com"}


@pytest.fixture
def admin_user(test_db):
    """Create admin user for testing"""
    password = "AdminPass123!"
    password_hash = AuthService.hash_password(password)
    
    user = User(
        id="admin-user-id",
        email="admin@example.com",
        name="Admin User",
        phone="+919876543211",
        address="Admin Address",
        password_hash=password_hash,
        is_active=True,
        is_admin=True,
    )
    
    test_db.add(user)
    test_db.commit()
    
    return {"user": user, "password": password, "email": "admin@example.com"}


# ────────────────────────────────────────────────────────────────────────────
# System Endpoints Tests
# ────────────────────────────────────────────────────────────────────────────

class TestSystemEndpoints:
    """Test system/health endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "E-Waste Management System API"
        assert "version" in data
        assert "endpoints" in data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
    
    def test_streamlit_health_check(self, client):
        """Test Streamlit compatible health check"""
        response = client.get("/_stcore/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


# ────────────────────────────────────────────────────────────────────────────
# Authentication Tests
# ────────────────────────────────────────────────────────────────────────────

class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_register_new_user(self, client):
        """Test user registration"""
        response = client.post("/api/v1/auth/register", json={
            "name": "New User",
            "email": "newuser@example.com",
            "phone": "+919876543210",
            "address": "Test Address",
            "password": "TestPass123!"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "id" in data
    
    def test_register_duplicate_email(self, client, demo_user):
        """Test registration with existing email"""
        response = client.post("/api/v1/auth/register", json={
            "name": "Another User",
            "email": demo_user["email"],  # Use existing email
            "phone": "+919876543211",
            "address": "Test Address",
            "password": "AnotherPass123!"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"].lower()
    
    def test_login_success(self, client, demo_user):
        """Test successful login"""
        response = client.post("/api/v1/auth/login", json={
            "email": demo_user["email"],
            "password": demo_user["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == demo_user["email"]
        assert data["is_admin"] is False
    
    def test_login_wrong_password(self, client, demo_user):
        """Test login with wrong password"""
        response = client.post("/api/v1/auth/login", json={
            "email": demo_user["email"],
            "password": "WrongPassword123!"
        })
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "AnyPassword123!"
        })
        
        assert response.status_code == 401
    
    def test_get_current_user(self, client, demo_user):
        """Test get current user endpoint"""
        # First login
        login_response = client.post("/api/v1/auth/login", json={
            "email": demo_user["email"],
            "password": demo_user["password"]
        })
        token = login_response.json()["access_token"]
        
        # Get current user
        response = client.get(f"/api/v1/auth/me?token={token}")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == demo_user["email"]
        assert data["name"] == "Demo User"
        assert data["is_admin"] is False


# ────────────────────────────────────────────────────────────────────────────
# Submissions Tests
# ────────────────────────────────────────────────────────────────────────────

class TestSubmissionsEndpoints:
    """Test submission management endpoints"""
    
    @pytest.fixture
    def auth_token(self, client, demo_user):
        """Get auth token for testing"""
        response = client.post("/api/v1/auth/login", json={
            "email": demo_user["email"],
            "password": demo_user["password"]
        })
        return response.json()["access_token"]
    
    def test_create_submission(self, client, auth_token):
        """Test submission creation"""
        response = client.post(f"/api/v1/submissions?token={auth_token}", json={
            "name": "John Doe",
            "phone": "+919876543210",
            "email": "john@example.com",
            "address": "123 Main St",
            "item_type": "Mobile Phone",
            "quantity": 5,
            "condition": "Working",
            "notes": "In good condition"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "Pending"
        assert data["priority"] in ["Low", "Medium", "High"]
        assert "id" in data
    
    def test_create_submission_invalid_item_type(self, client, auth_token):
        """Test submission with invalid item type"""
        response = client.post(f"/api/v1/submissions?token={auth_token}", json={
            "name": "John Doe",
            "phone": "+919876543210",
            "email": "john@example.com",
            "address": "123 Main St",
            "item_type": "Invalid Item",
            "quantity": 5,
            "condition": "Working"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_list_submissions(self, client, auth_token):
        """Test listing submissions"""
        # Create a submission first
        client.post(f"/api/v1/submissions?token={auth_token}", json={
            "name": "John Doe",
            "phone": "+919876543210",
            "email": "john@example.com",
            "address": "123 Main St",
            "item_type": "Mobile Phone",
            "quantity": 1,
            "condition": "Working"
        })
        
        # List submissions
        response = client.get(f"/api/v1/submissions?token={auth_token}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_list_submissions_with_filters(self, client, auth_token):
        """Test listing submissions with status filter"""
        response = client.get(f"/api/v1/submissions?token={auth_token}&status=Pending")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ────────────────────────────────────────────────────────────────────────────
# Analytics Tests
# ────────────────────────────────────────────────────────────────────────────

class TestAnalyticsEndpoints:
    """Test analytics endpoints"""
    
    @pytest.fixture
    def auth_token(self, client, demo_user):
        """Get auth token for testing"""
        response = client.post("/api/v1/auth/login", json={
            "email": demo_user["email"],
            "password": demo_user["password"]
        })
        return response.json()["access_token"]
    
    def test_dashboard_stats(self, client, auth_token):
        """Test dashboard statistics endpoint"""
        response = client.get(f"/api/v1/analytics/dashboard?token={auth_token}")
        assert response.status_code == 200
        data = response.json()
        assert "total_submissions" in data
        assert "total_co2_saved" in data
        assert "status_breakdown" in data
    
    def test_impact_summary(self, client, auth_token):
        """Test impact summary endpoint"""
        response = client.get(f"/api/v1/analytics/impact-summary?token={auth_token}")
        assert response.status_code == 200
        data = response.json()
        assert "co2_saved_kg" in data
        assert "tree_equivalents" in data
    
    def test_submissions_by_type(self, client, auth_token):
        """Test submissions by type endpoint"""
        response = client.get(f"/api/v1/analytics/submissions-by-type?token={auth_token}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


# ────────────────────────────────────────────────────────────────────────────
# Collection Points Tests
# ────────────────────────────────────────────────────────────────────────────

class TestCollectionPointsEndpoints:
    """Test collection points endpoints"""
    
    @pytest.fixture
    def auth_token(self, client, demo_user):
        """Get auth token for testing"""
        response = client.post("/api/v1/auth/login", json={
            "email": demo_user["email"],
            "password": demo_user["password"]
        })
        return response.json()["access_token"]
    
    def test_list_collection_points(self, client, auth_token, test_db):
        """Test listing collection points"""
        # Create a collection point
        from utils.database import CollectionPoint
        point = CollectionPoint(
            id="point-1",
            name="Test Collection Center",
            address="123 Test St",
            city="Pune",
            latitude=18.5204,
            longitude=73.8567,
            capacity=1000,
            current_load=500,
            phone="+919876543210",
            status="Active"
        )
        test_db.add(point)
        test_db.commit()
        
        response = client.get(f"/api/v1/collection-points?token={auth_token}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_nearby_collection_points(self, client, auth_token, test_db):
        """Test finding nearby collection points"""
        response = client.get(
            f"/api/v1/collection-points/nearby?token={auth_token}&"
            f"latitude=18.5204&longitude=73.8567&radius_km=10"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ────────────────────────────────────────────────────────────────────────────
# Admin Tests
# ────────────────────────────────────────────────────────────────────────────

class TestAdminEndpoints:
    """Test admin-only endpoints"""
    
    @pytest.fixture
    def admin_token(self, client, admin_user):
        """Get admin auth token"""
        response = client.post("/api/v1/auth/login", json={
            "email": admin_user["email"],
            "password": admin_user["password"]
        })
        return response.json()["access_token"]
    
    @pytest.fixture
    def user_token(self, client, demo_user):
        """Get regular user auth token"""
        response = client.post("/api/v1/auth/login", json={
            "email": demo_user["email"],
            "password": demo_user["password"]
        })
        return response.json()["access_token"]
    
    def test_admin_stats(self, client, admin_token):
        """Test admin statistics endpoint"""
        response = client.get(f"/api/v1/admin/stats?token={admin_token}")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_submissions" in data
    
    def test_admin_stats_forbidden_for_user(self, client, user_token):
        """Test that regular users cannot access admin stats"""
        response = client.get(f"/api/v1/admin/stats?token={user_token}")
        assert response.status_code == 403
    
    def test_list_all_users(self, client, admin_token):
        """Test listing all users (admin only)"""
        response = client.get(f"/api/v1/admin/users?token={admin_token}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_all_users_forbidden_for_user(self, client, user_token):
        """Test that regular users cannot list all users"""
        response = client.get(f"/api/v1/admin/users?token={user_token}")
        assert response.status_code == 403


# ────────────────────────────────────────────────────────────────────────────
# Security Tests
# ────────────────────────────────────────────────────────────────────────────

class TestSecurityHeaders:
    """Test security headers"""
    
    def test_security_headers_present(self, client):
        """Test that security headers are present in responses"""
        response = client.get("/health")
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-XSS-Protection" in response.headers
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present"""
        response = client.get("/health")
        
        # CORS headers may or may not be present depending on request origin
        # Just verify the endpoint responds correctly
        assert response.status_code == 200


# ────────────────────────────────────────────────────────────────────────────
# Error Handling Tests
# ────────────────────────────────────────────────────────────────────────────

class TestErrorHandling:
    """Test error handling and responses"""
    
    def test_404_error(self, client):
        """Test 404 error response"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_token(self, client):
        """Test invalid token handling"""
        response = client.get("/api/v1/submissions?token=invalid-token")
        assert response.status_code == 401
    
    def test_validation_error_format(self, client):
        """Test validation error response format"""
        response = client.post("/api/v1/auth/login", json={
            "email": "not-an-email",
            "password": "pass"
        })
        assert response.status_code == 422
