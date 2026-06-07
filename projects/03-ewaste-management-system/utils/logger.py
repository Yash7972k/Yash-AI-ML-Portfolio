"""
Logging setup for E-Waste Management System
"""
import logging
import logging.handlers
from pathlib import Path
from config import config
from datetime import datetime

# Create logs directory if it doesn't exist
config.LOG_DIR.mkdir(exist_ok=True)

def setup_logger(name: str) -> logging.Logger:
    """Setup logger with file and console handlers"""
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Console handler with UTF-8 encoding for Windows compatibility
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    console_handler.stream.reconfigure(encoding='utf-8') if hasattr(console_handler.stream, 'reconfigure') else None
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler (rotating)
    log_file = config.LOG_DIR / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Create app logger
app_logger = setup_logger("ewaste_app")

# Module loggers
db_logger = setup_logger("database")
auth_logger = setup_logger("auth")
email_logger = setup_logger("email")
payment_logger = setup_logger("payment")
