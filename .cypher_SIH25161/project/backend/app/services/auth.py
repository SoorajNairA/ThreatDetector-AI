"""Authentication utilities"""
from typing import Optional
from fastapi import HTTPException, Security, Request, Header
from fastapi.security import APIKeyHeader
from app.config import settings
from app.logging_config import get_logger
from app.services.supabase_client import verify_api_key, verify_supabase_token

logger = get_logger(__name__)

# API key header
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def get_current_user(
    api_key: Optional[str] = Security(api_key_header),
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Verify API key or Supabase Auth token and return user information.
    
    Supports two authentication methods:
    1. API key via x-api-key header (for existing users with keys)
    2. Supabase JWT token via Authorization header (for new users creating their first key)
    
    Args:
        api_key: API key from x-api-key header
        authorization: Bearer token from Authorization header
        
    Returns:
        Dictionary with user_id and other user info
        
    Raises:
        HTTPException: If authentication fails
    """
    # Try Supabase Auth token first (Authorization: Bearer <token>)
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        user_data = verify_supabase_token(token)
        if user_data:
            logger.debug(f"Authenticated via Supabase token: {user_data['user_id']}")
            return {
                "user_id": user_data["user_id"],
                "email": user_data.get("email"),
                "is_global": False,
                "auth_method": "supabase"
            }
    
    # Try API key authentication
    if api_key:
        # Check if it's empty or whitespace only
        if not api_key.strip():
            logger.warning("Empty API key provided")
            raise HTTPException(status_code=403, detail="Invalid API key: empty value")
        
        # If global API_KEY is set (backward compatibility), allow it
        if settings.API_KEY and api_key == settings.API_KEY:
            logger.debug("Using global API key (backward compatibility)")
            return {
                "user_id": None,
                "is_global": True,
                "auth_method": "global_key"
            }
        
        # Verify API key against database
        key_data = verify_api_key(api_key)
        if key_data:
            logger.debug(f"Authenticated via API key: {key_data['user_id']}")
            return {
                "user_id": key_data["user_id"],
                "key_id": key_data["id"],
                "key_name": key_data.get("name"),
                "is_global": False,
                "auth_method": "api_key"
            }
        else:
            # API key provided but invalid - reject immediately
            logger.warning(f"Invalid API key attempted: {api_key[:10]}...")
            raise HTTPException(status_code=403, detail="Invalid API key")
    
    # No valid authentication provided
    logger.warning("Authentication required but not provided")
    raise HTTPException(
        status_code=401, 
        detail="Authentication required. Provide either x-api-key or Authorization header"
    )
