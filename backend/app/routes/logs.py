"""Logs endpoint - fetch user's analysis history"""
from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.services.auth import get_current_user
from app.services.supabase_client import supabase
from app.config import settings
from app.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/logs", tags=["logs"])
async def get_user_logs(
    current_user: dict = Depends(get_current_user),
    limit: int = 100
) -> Dict[str, Any]:
    """
    Fetch analysis logs for the current user.
    
    Returns detailed history of all threat analyses performed by this user,
    including timestamps, analyzed text, risk scores, and classifier results.
    
    Args:
        current_user: User info from API key (injected)
        limit: Maximum number of logs to return (default: 100)
        
    Returns:
        Dictionary containing array of log entries
    """
    user_id = current_user.get("user_id")
    logger.info(f"Fetching logs for user: {user_id}")
    
    try:
        # Query threats table for user's analysis history
        query = (
            supabase.table(settings.SUPABASE_THREATS_TABLE)
            .select("*")
            .eq("user_id", user_id)
            .order("timestamp", desc=True)
            .limit(limit)
        )
        
        response = query.execute()
        logs = response.data or []
        
        logger.info(f"Found {len(logs)} logs for user {user_id}")
        
        return {
            "logs": logs,
            "count": len(logs)
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch logs for user {user_id}: {e}")
        raise
