"""
Rate Limiting Configuration
Implements request rate limiting to prevent abuse and DDoS attacks
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


# Custom exception handler for rate limit exceeded
async def rate_limit_exception_handler(request, exc: RateLimitExceeded):
    """Handle rate limit exceeded exceptions"""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate limit exceeded",
            "detail": str(exc.detail),
            "status_code": 429,
        },
    )


# Rate limit configurations
class RateLimits:
    """Rate limiting tiers"""
    
    # Authentication endpoints - stricter limits (prevent brute force)
    AUTH_LOGIN = "5/minute"              # 5 attempts per minute
    AUTH_REGISTER = "10/hour"             # 10 new accounts per hour
    
    # Standard endpoints - moderate limits
    SUBMISSIONS_READ = "100/hour"         # 100 reads per hour
    SUBMISSIONS_WRITE = "50/hour"         # 50 writes per hour
    
    # Analytics - more relaxed
    ANALYTICS = "200/hour"                # 200 queries per hour
    
    # Collection points - relaxed (read-only)
    COLLECTION_POINTS = "500/hour"        # 500 queries per hour
    
    # Admin - strict (sensitive operations)
    ADMIN_OPERATIONS = "10/hour"          # 10 admin ops per hour
    
    # Health check - unlimited
    HEALTH_CHECK = None                   # No limit


def get_rate_limit_config() -> dict:
    """Get rate limit configuration as dictionary"""
    return {
        "auth_login": RateLimits.AUTH_LOGIN,
        "auth_register": RateLimits.AUTH_REGISTER,
        "submissions_read": RateLimits.SUBMISSIONS_READ,
        "submissions_write": RateLimits.SUBMISSIONS_WRITE,
        "analytics": RateLimits.ANALYTICS,
        "collection_points": RateLimits.COLLECTION_POINTS,
        "admin": RateLimits.ADMIN_OPERATIONS,
    }
