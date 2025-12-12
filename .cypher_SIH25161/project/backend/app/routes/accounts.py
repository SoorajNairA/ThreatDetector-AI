"""
Account and API Key Management Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from typing import Optional, List
from app.services.account_service import get_account_service
from app.services.audit import log_audit_event
from app.middleware.auth import get_account_from_api_key, get_current_account_id
from app.logging_config import get_logger

router = APIRouter(prefix="/accounts", tags=["accounts"])
logger = get_logger(__name__)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class CreateAccountRequest(BaseModel):
    """Request to create a new account"""
    name: str = Field(..., description="Account display name")


class CreateAccountResponse(BaseModel):
    """Response with new account and first API key"""
    account_id: str
    account_name: str
    api_key: str  # Only returned once!
    message: str


class CreateAPIKeyRequest(BaseModel):
    """Request to create a new API key"""
    name: Optional[str] = Field(None, description="Friendly name for the key")


class CreateAPIKeyResponse(BaseModel):
    """Response with new API key"""
    key_id: str
    api_key: str  # Only returned once!
    prefix: str
    name: Optional[str]
    created_at: str
    message: str


class APIKeyInfo(BaseModel):
    """API key information (without the actual key)"""
    id: str
    prefix: str
    name: Optional[str]
    created_at: str
    last_used: Optional[str]
    revoked: bool
    revoked_at: Optional[str]


class RevokeAPIKeyResponse(BaseModel):
    """Response after revoking a key"""
    message: str
    key_id: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/create", response_model=CreateAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(request: CreateAccountRequest, req: Request):
    """
    Create a new account with first API key (bootstrap endpoint)
    
    This is the only endpoint that doesn't require authentication.
    Returns the account ID and first API key.
    """
    try:
        account_service = get_account_service()
        
        # Create account
        account = account_service.create_account(request.name)
        
        # Generate first API key
        api_key, key_record = account_service.generate_api_key(
            account["id"], 
            name="Initial API Key"
        )
        
        # Log account creation
        await log_audit_event(
            account_id=account["id"],
            event_type="account_created",
            metadata={"name": request.name},
            request=req
        )
        
        return CreateAccountResponse(
            account_id=account["id"],
            account_name=account["name"],
            api_key=api_key,
            message="Account created successfully. Save your API key - it won't be shown again!"
        )
        
    except Exception as e:
        logger.error(f"Failed to create account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create account: {str(e)}"
        )


@router.post("/api-keys", response_model=CreateAPIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: CreateAPIKeyRequest,
    req: Request,
    account_info: dict = Depends(get_account_from_api_key)
):
    """
    Create a new API key for the authenticated account
    
    Requires: x-api-key header with valid API key
    """
    try:
        account_service = get_account_service()
        account_id = account_info["account_id"]
        
        # Generate new API key
        api_key, key_record = account_service.generate_api_key(
            account_id,
            name=request.name
        )
        
        # Log key creation
        await log_audit_event(
            account_id=account_id,
            event_type="api_key_created",
            metadata={"key_id": key_record["id"], "name": request.name},
            request=req
        )
        
        return CreateAPIKeyResponse(
            key_id=key_record["id"],
            api_key=api_key,
            prefix=key_record["prefix"],
            name=key_record.get("name"),
            created_at=key_record["created_at"],
            message="API key created successfully. Save it - it won't be shown again!"
        )
        
    except Exception as e:
        logger.error(f"Failed to create API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create API key: {str(e)}"
        )


@router.get("/api-keys", response_model=List[APIKeyInfo])
async def list_api_keys(
    req: Request,
    account_info: dict = Depends(get_account_from_api_key)
):
    """
    List all API keys for the authenticated account
    
    Requires: x-api-key header with valid API key
    """
    try:
        account_service = get_account_service()
        account_id = account_info["account_id"]
        
        keys = account_service.list_api_keys(account_id)
        
        return [APIKeyInfo(**key) for key in keys]
        
    except Exception as e:
        logger.error(f"Failed to list API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list API keys: {str(e)}"
        )


@router.delete("/api-keys/{key_id}", response_model=RevokeAPIKeyResponse)
async def revoke_api_key(
    key_id: str,
    req: Request,
    account_info: dict = Depends(get_account_from_api_key)
):
    """
    Revoke an API key
    
    Requires: x-api-key header with valid API key
    Note: You cannot revoke the key you're currently using
    """
    try:
        account_service = get_account_service()
        account_id = account_info["account_id"]
        current_key_id = account_info["key_id"]
        
        # Prevent revoking current key
        if key_id == current_key_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot revoke the API key you're currently using"
            )
        
        # Revoke key
        success = account_service.revoke_api_key(key_id, account_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found or already revoked"
            )
        
        # Log revocation
        await log_audit_event(
            account_id=account_id,
            event_type="api_key_revoked",
            metadata={"key_id": key_id},
            request=req
        )
        
        return RevokeAPIKeyResponse(
            message="API key revoked successfully",
            key_id=key_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke API key: {str(e)}"
        )
