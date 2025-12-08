"""API Key management endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.supabase_client import create_api_key, list_user_api_keys, deactivate_api_key
from app.services.auth import get_current_user
from app.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


class CreateKeyRequest(BaseModel):
    """Request to create new API key"""
    name: Optional[str] = "Default Key"


class APIKeyResponse(BaseModel):
    """API key response"""
    id: str
    api_key: Optional[str] = None  # Only returned on creation
    name: str
    is_active: bool
    created_at: str
    last_used_at: Optional[str] = None


@router.post("/keys", response_model=APIKeyResponse, tags=["keys"])
async def create_new_key(
    request: CreateKeyRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new API key for the authenticated user.
    
    Requires authentication via existing API key or Supabase Auth.
    
    Args:
        request: CreateKeyRequest with optional key name
        current_user: User info (injected)
        
    Returns:
        APIKeyResponse with the newly created API key (only shown once)
    """
    user_id = current_user.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=403, detail="Cannot create keys with global API key")
    
    logger.info(f"Creating new API key for user: {user_id}")
    
    try:
        key_data = create_api_key(user_id, request.name)
        return {
            "id": key_data["id"],
            "api_key": key_data["api_key"],  # Only returned here
            "name": key_data["name"],
            "is_active": key_data["is_active"],
            "created_at": key_data["created_at"],
            "last_used_at": key_data.get("last_used_at")
        }
    except Exception as e:
        logger.error(f"Failed to create API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to create API key")


@router.get("/keys", response_model=List[APIKeyResponse], tags=["keys"])
async def list_keys(current_user: dict = Depends(get_current_user)):
    """
    List all API keys for the authenticated user.
    
    Note: API key values are not returned (only shown on creation).
    
    Args:
        current_user: User info (injected)
        
    Returns:
        List of APIKeyResponse objects
    """
    user_id = current_user.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=403, detail="Cannot list keys with global API key")
    
    logger.info(f"Listing API keys for user: {user_id}")
    
    try:
        keys = list_user_api_keys(user_id)
        return [
            {
                "id": key["id"],
                "name": key["name"],
                "is_active": key["is_active"],
                "created_at": key["created_at"],
                "last_used_at": key.get("last_used_at")
            }
            for key in keys
        ]
    except Exception as e:
        logger.error(f"Failed to list API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to list API keys")


@router.delete("/keys/{key_id}", tags=["keys"])
async def delete_key(
    key_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Deactivate an API key.
    
    Args:
        key_id: ID of the key to deactivate
        current_user: User info (injected)
        
    Returns:
        Success message
    """
    user_id = current_user.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=403, detail="Cannot delete keys with global API key")
    
    logger.info(f"Deactivating API key {key_id} for user: {user_id}")
    
    try:
        deactivate_api_key(key_id, user_id)
        return {"message": "API key deactivated successfully"}
    except Exception as e:
        logger.error(f"Failed to deactivate API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to deactivate API key")
