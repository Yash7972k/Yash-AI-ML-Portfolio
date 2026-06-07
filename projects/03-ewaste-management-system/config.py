"""
Configuration management for E-Waste Management System
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    
    # App
    APP_NAME = os.getenv("APP_NAME", "E-Waste Management System")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./ewaste.db"  # Default to SQLite for development
    )
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # Email
    EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "gmail")
    GMAIL_EMAIL = os.getenv("GMAIL_EMAIL", "")
    GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
    
    # SMS
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Payment
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
    
    # Maps
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
    
    # Location
    DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Pune")
    DEFAULT_LATITUDE = float(os.getenv("DEFAULT_LATITUDE", "18.5204"))
    DEFAULT_LONGITUDE = float(os.getenv("DEFAULT_LONGITUDE", "73.8567"))
    
    # Collection Points
    MAX_COLLECTION_POINTS = int(os.getenv("MAX_COLLECTION_POINTS", "50"))
    MIN_CAPACITY = int(os.getenv("MIN_CAPACITY", "100"))
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOG_DIR = BASE_DIR / "logs"
    MODEL_DIR = BASE_DIR / "model"
    
    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    MODEL_DIR.mkdir(exist_ok=True)

# Create config instance
config = Config()
