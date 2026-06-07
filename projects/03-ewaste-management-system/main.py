"""
E-Waste Management System - REST API
FastAPI application for e-waste submission, tracking, and analytics

Usage:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

API Documentation:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import logging
from datetime import datetime

# Import utilities
from config import Config
from utils.database import SessionLocal, init_db, engine, Base, CollectionPoint
from utils.logger import setup_logger, app_logger
from utils.auth import AuthService
from utils.models import LoginRequest, UserCreate, EWasteSubmissionCreate
from utils.rate_limiting import limiter, rate_limit_exception_handler, get_rate_limit_config

# Import routers (we'll create these)
from api.routes import auth, submissions, analytics, collection_points, admin

# ────────────────────────────────────────────────────────────────────────────
# Lifecycle Events
# ────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    app_logger.info("[STARTUP] E-Waste API starting up...")
    try:
        Base.metadata.create_all(bind=engine)
        app_logger.info("[SUCCESS] Database initialized")
        
        # Seed collection points if they don't exist
        db = SessionLocal()
        try:
            existing_points = db.query(CollectionPoint).first()
            if not existing_points:
                collection_points = [
                    CollectionPoint(
                        name="Pune Central Recycling Center",
                        address="123 Eco Park Road, Pune",
                        city="Pune",
                        latitude=18.5204,
                        longitude=73.8567,
                        capacity=1000,
                        phone="+91-9876543210",
                        status="Active"
                    ),
                    CollectionPoint(
                        name="Baner E-Waste Collection Hub",
                        address="456 Tech Street, Baner, Pune",
                        city="Pune",
                        latitude=18.5596,
                        longitude=73.7997,
                        capacity=800,
                        phone="+91-9876543211",
                        status="Active"
                    ),
                    CollectionPoint(
                        name="Hinjewadi Electronics Recovery Center",
                        address="789 Innovation Drive, Hinjewadi, Pune",
                        city="Pune",
                        latitude=18.5912,
                        longitude=73.7653,
                        capacity=1200,
                        phone="+91-9876543212",
                        status="Active"
                    ),
                    CollectionPoint(
                        name="Wakad Green Recycling Station",
                        address="321 Green Street, Wakad, Pune",
                        city="Pune",
                        latitude=18.5889,
                        longitude=73.8288,
                        capacity=600,
                        phone="+91-9876543213",
                        status="Active"
                    ),
                    CollectionPoint(
                        name="Viman Nagar E-Waste Drop Point",
                        address="654 Airport Road, Viman Nagar, Pune",
                        city="Pune",
                        latitude=18.5674,
                        longitude=73.9170,
                        capacity=500,
                        phone="+91-9876543214",
                        status="Active"
                    ),
                ]
                db.add_all(collection_points)
                db.commit()
                app_logger.info(f"[SUCCESS] Seeded {len(collection_points)} collection points")
        finally:
            db.close()
    except Exception as e:
        app_logger.error(f"[ERROR] Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    app_logger.info("[SHUTDOWN] E-Waste API shutting down...")


# ────────────────────────────────────────────────────────────────────────────
# FastAPI Application
# ────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="E-Waste Management System API",
    description="Production-ready REST API for e-waste collection, tracking, and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add rate limiter state to app
app.state.limiter = limiter
app.add_exception_handler(429, rate_limit_exception_handler)

# ────────────────────────────────────────────────────────────────────────────
# Security Headers Middleware (Must come before CORS)
# ────────────────────────────────────────────────────────────────────────────

@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Prevent clickjacking attacks
    response.headers["X-Frame-Options"] = "DENY"
    
    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Enable HSTS (for HTTPS only)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Content Security Policy - allow swagger UI & redoc
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net fonts.googleapis.com; font-src 'self' fonts.gstatic.com cdn.jsdelivr.net"
    
    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

# ────────────────────────────────────────────────────────────────────────────
# CORS Middleware (Allow frontend & mobile apps)
# ────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React frontend (dev)
        "http://localhost:8501",      # Streamlit app (dev)
        "http://localhost:8000",      # API docs (dev)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8000",      # API docs (dev)
        # Production origins - update these
        # "https://yourdomain.com",
        # "https://app.yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=600,  # Cache CORS preflight for 10 minutes
)

# ────────────────────────────────────────────────────────────────────────────
# Dependency: Get Database Session
# ────────────────────────────────────────────────────────────────────────────

def get_db():
    """Dependency to inject database session into route handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ────────────────────────────────────────────────────────────────────────────
# Health Check & Info Endpoints
# ────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["System"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": "E-Waste Management System API",
        "version": "1.0.0",
        "status": "🟢 Running",
        "timestamp": datetime.now().isoformat(),
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
        "endpoints": {
            "health": "/health",
            "auth": "/api/v1/auth",
            "submissions": "/api/v1/submissions",
            "analytics": "/api/v1/analytics",
            "collection_points": "/api/v1/collection-points",
            "admin": "/api/v1/admin",
        }
    }


@app.get("/health", tags=["System"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        db.execute("SELECT 1")
        return {
            "status": "🟢 Healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "🟢 Connected",
            "version": "1.0.0",
        }
    except Exception as e:
        app_logger.error(f"Health check failed: {e}")
        return {
            "status": "🔴 Unhealthy",
            "timestamp": datetime.now().isoformat(),
            "database": "🔴 Disconnected",
            "error": str(e),
        }, 503


@app.get("/_stcore/health", tags=["System"])
async def streamlit_health_check():
    """Streamlit-compatible health check endpoint."""
    return JSONResponse({"status": "ok"})


# ────────────────────────────────────────────────────────────────────────────
# Include API Routers
# ────────────────────────────────────────────────────────────────────────────

# Authentication routes
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

# E-Waste submission routes
app.include_router(
    submissions.router,
    prefix="/api/v1/submissions",
    tags=["Submissions"],
)

# Analytics routes
app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["Analytics"],
)

# Collection points routes
app.include_router(
    collection_points.router,
    prefix="/api/v1/collection-points",
    tags=["Collection Points"],
)

# Admin routes
app.include_router(
    admin.router,
    prefix="/api/v1/admin",
    tags=["Admin"],
)

# ────────────────────────────────────────────────────────────────────────────
# Exception Handlers
# ────────────────────────────────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    app_logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat(),
        },
    )

# ────────────────────────────────────────────────────────────────────────────
# Entry Point
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    
    app_logger.info("🚀 Starting E-Waste Management API...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
