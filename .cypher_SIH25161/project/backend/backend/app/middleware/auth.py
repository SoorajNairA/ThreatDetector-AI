"""
Authentication Middleware
Validates API keys and attaches account context to requests
"""
from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional, Dict, Any
from app.services.account_service import get_account_service
from app.services.audit import log_audit_event
from app.logging_config import get_logger

logger = get_logger(__name__)

# Header scheme for API key
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def get_account_from_api_key(request: Request) -> Dict[str, Any]:
    """
    Middleware dependency to validate API key and attach account context
    
    Extracts x-api-key header, validates it, and returns account info
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dict with account_id and key_id
        
    Raises:
        HTTPException: 401 if key missing, 403 if invalid
    """
    # Extract API key from header
    api_key = request.headers.get("x-api-key")
    
    if not api_key:
        logger.warning("Missing x-api-key header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    # Validate API key
    account_service = get_account_service()
    account_info = account_service.validate_api_key(api_key)
    
    if not account_info:
        logger.warning(f"Invalid API key: {api_key[:8]}...")
        
        # Log failed authentication attempt
        await log_audit_event(
            account_id=None,
            event_type="auth_failed",
            metadata={"reason": "invalid_api_key"},
            request=request
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or revoked API key"
        )
    
    # Attach account context to request state
    request.state.account_id = account_info["account_id"]
    request.state.key_id = account_info["key_id"]
    
    logger.info(f"Authenticated request from account: {account_info['account_id']}")
    
    return account_info


def get_current_account_id(request: Request) -> str:
    """
    Extract account_id from request state
    
    Args:
        request: FastAPI request object
        
    Returns:
        Account UUID string
        
    Raises:
        HTTPException: If account_id not in state
    """
    account_id = getattr(request.state, "account_id", None)
    
    if not account_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return account_id


def get_current_key_id(request: Request) -> str:
    """
    Extract key_id from request state
    
    Args:
        request: FastAPI request object
        
    Returns:
        API key UUID string
        
    Raises:
        HTTPException: If key_id not in state
    """
    key_id = getattr(request.state, "key_id", None)
    
    if not key_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return key_id


# ============================================================================
# OPTIONAL: Global middleware for all routes
# ============================================================================

async def authentication_middleware(request: Request, call_next):
    """
    Global middleware to validate API keys on all protected routes
    
    Skip authentication for:
    - /health
    - /docs
    - /openapi.json
    - /accounts/create (bootstrap endpoint)
    
    Args:
        request: FastAPI request
        call_next: Next middleware/handler
        
    Returns:
        Response from next handler
    """
    # Public endpoints that don't require authentication
    public_paths = ["/health", "/docs", "/openapi.json", "/redoc", "/accounts/create"]
    
    if request.url.path in public_paths or request.url.path.startswith("/static"):
        return await call_next(request)
    
    # Validate API key for all other routes
    try:
        await get_account_from_api_key(request)
    except HTTPException as e:
        # Return error response
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        )
    
    # Continue to next handler
    response = await call_next(request)
    return response
