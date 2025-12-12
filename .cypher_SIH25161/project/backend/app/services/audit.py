"""
Audit Logging Service
Records security events and API usage
"""
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import Request
from app.services.supabase_client import supabase
from app.logging_config import get_logger

logger = get_logger(__name__)


async def log_audit_event(
    account_id: Optional[str],
    event_type: str,
    metadata: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
) -> None:
    """
    Log an audit event
    
    Args:
        account_id: Account UUID (None for unauthenticated events)
        event_type: Event type (e.g., 'api_key_created', 'analyze_called')
        metadata: Additional event data
        request: FastAPI request object (for IP/UA extraction)
    """
    try:
        supabase_client = supabase
        
        # Extract request info
        ip_address = None
        user_agent = None
        
        if request:
            # Get client IP
            ip_address = request.client.host if request.client else None
            
            # Get user agent
            user_agent = request.headers.get("user-agent")
        
        # Create audit record
        audit_record = {
            "account_id": account_id,
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        # Insert into audit log
        supabase_client.table("audit_log").insert(audit_record).execute()
        
        logger.info(f"Audit log: {event_type} for account {account_id or 'N/A'}")
        
    except Exception as e:
        # Never fail the request due to audit logging
        logger.error(f"Failed to log audit event: {e}")


def get_audit_log(account_id: str, limit: int = 100) -> list:
    """
    Get audit log for an account
    
    Args:
        account_id: Account UUID
        limit: Max number of records to return
        
    Returns:
        List of audit log records
    """
    try:
        result = supabase.table("audit_log").select("*").eq(
            "account_id", account_id
        ).order("timestamp", desc=True).limit(limit).execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        logger.error(f"Failed to get audit log: {e}")
        return []
