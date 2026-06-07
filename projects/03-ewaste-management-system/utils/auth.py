"""
Authentication and authorization utilities
"""
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional, Dict
from config import config
from utils.logger import auth_logger

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class AuthService:
    """Authentication service for user login and token management"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        try:
            return pwd_context.hash(password)
        except Exception as e:
            auth_logger.error(f"Password hashing failed: {str(e)}")
            raise
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            auth_logger.error(f"Password verification failed: {str(e)}")
            return False
    
    @staticmethod
    def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        try:
            to_encode = data.copy()
            
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(hours=config.JWT_EXPIRATION_HOURS)
            
            to_encode.update({"exp": expire, "iat": datetime.utcnow()})
            
            encoded_jwt = jwt.encode(
                to_encode,
                config.SECRET_KEY,
                algorithm=config.JWT_ALGORITHM
            )
            auth_logger.info(f"Access token created for user: {data.get('sub')}")
            return encoded_jwt
        except Exception as e:
            auth_logger.error(f"Token creation failed: {str(e)}")
            raise
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(
                token,
                config.SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            auth_logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            auth_logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            auth_logger.error(f"Token verification failed: {str(e)}")
            return None
    
    @staticmethod
    def generate_refresh_token(user_id: int) -> str:
        """Generate refresh token"""
        try:
            data = {"sub": str(user_id), "type": "refresh"}
            token = jwt.encode(
                {
                    **data,
                    "exp": datetime.utcnow() + timedelta(days=7),
                    "iat": datetime.utcnow()
                },
                config.SECRET_KEY,
                algorithm=config.JWT_ALGORITHM
            )
            return token
        except Exception as e:
            auth_logger.error(f"Refresh token generation failed: {str(e)}")
            raise

class RoleBasedAccess:
    """Role-based access control"""
    
    ROLES = {
        "admin": ["read", "write", "delete", "manage_users", "manage_payments"],
        "staff": ["read", "write"],
        "user": ["read"]
    }
    
    @staticmethod
    def has_permission(role: str, action: str) -> bool:
        """Check if role has permission for action"""
        if role not in RoleBasedAccess.ROLES:
            return False
        return action in RoleBasedAccess.ROLES[role]
    
    @staticmethod
    def get_permissions(role: str) -> list:
        """Get all permissions for a role"""
        return RoleBasedAccess.ROLES.get(role, [])

# Quick utility functions
def hash_pwd(pwd: str) -> str:
    """Quick password hash"""
    return AuthService.hash_password(pwd)

def verify_pwd(pwd: str, hash_pwd: str) -> bool:
    """Quick password verify"""
    return AuthService.verify_password(pwd, hash_pwd)

def create_token(user_id: int, is_admin: bool = False) -> str:
    """Quick token creation"""
    return AuthService.create_access_token({
        "sub": str(user_id),
        "is_admin": is_admin
    })

def verify_token_payload(token: str) -> Optional[Dict]:
    """Quick token verification"""
    return AuthService.verify_token(token)
