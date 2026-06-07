"""
Database setup and ORM models
Supports both SQLite (development) and PostgreSQL (production)
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from config import config
from utils.logger import db_logger
import uuid

# Create database engine
engine = create_engine(
    config.DATABASE_URL,
    echo=config.DEBUG,
    pool_pre_ping=True,  # Verify connections before using
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== ORM MODELS ====================

class User(Base):
    """User database model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    address = Column(String(500), nullable=False)
    city = Column(String(50), default="Pune")
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"

class EWasteSubmission(Base):
    """E-waste submission database model"""
    __tablename__ = "ewaste_submissions"
    
    id = Column(String(20), primary_key=True, default=lambda: f"EW{uuid.uuid4().hex[:8].upper()}")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    address = Column(String(500), nullable=False)
    item_type = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    condition = Column(String(50), nullable=False)
    status = Column(String(50), default="Pending", index=True)  # Pending, Collected, Recycled
    priority = Column(String(50), nullable=False)  # High, Medium, Low
    hazard_level = Column(String(50), nullable=False)  # Low, Medium, High, Critical
    co2_saved = Column(Float, default=0)
    weight_kg = Column(Float, nullable=False)
    recycle_value = Column(Float, default=0)
    collection_point = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<EWasteSubmission(id={self.id}, status={self.status}, priority={self.priority})>"

class CollectionPoint(Base):
    """Collection point database model"""
    __tablename__ = "collection_points"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(500), nullable=False)
    city = Column(String(50), default="Pune", index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=False)
    current_load = Column(Integer, default=0)
    phone = Column(String(20), nullable=False)
    status = Column(String(50), default="Active", index=True)  # Active, Full, Closed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CollectionPoint(id={self.id}, name={self.name}, status={self.status})>"

class Payment(Base):
    """Payment database model"""
    __tablename__ = "payments"
    
    id = Column(String(20), primary_key=True, default=lambda: f"PAY{uuid.uuid4().hex[:8].upper()}")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submission_id = Column(String(20), ForeignKey("ewaste_submissions.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(50), default="Pending", index=True)  # Pending, Completed, Failed
    razorpay_order_id = Column(String(100), nullable=True, unique=True)
    razorpay_payment_id = Column(String(100), nullable=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Payment(id={self.id}, status={self.status}, amount={self.amount})>"

class AuditLog(Base):
    """Audit log for tracking all changes"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, entity_type={self.entity_type})>"

# ==================== DATABASE UTILITIES ====================

def init_db():
    """Initialize database - create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        db_logger.info("Database initialized successfully")
    except Exception as e:
        db_logger.error(f"Failed to initialize database: {str(e)}")
        raise

def get_db() -> Session:
    """Get database session for dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def reset_db():
    """Reset database - drop all tables (use with caution!)"""
    try:
        Base.metadata.drop_all(bind=engine)
        db_logger.warning("All database tables dropped")
    except Exception as e:
        db_logger.error(f"Failed to reset database: {str(e)}")
        raise

# Initialize database on import
if __name__ == "__main__":
    init_db()
    db_logger.info("Database setup complete")
