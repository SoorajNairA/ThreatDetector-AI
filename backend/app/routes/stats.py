"""Statistics endpoint"""
from fastapi import APIRouter, Depends
from app.models import StatsResponse
from app.services.supabase_client import fetch_threat_stats
from app.services.auth import get_current_user
from app.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/stats", response_model=StatsResponse, tags=["stats"])
async def get_stats(current_user: dict = Depends(get_current_user)):
    """
    Get aggregate statistics from threats table.
    
    Returns summary counts for the authenticated user including:
    - Total threats
    - Counts by risk level (high, medium, low)
    - Number of unique actors
    - Timestamp of most recent threat
    
    Args:
        current_user: User info from API key (injected)
        
    Returns:
        StatsResponse with aggregate statistics
    """
    user_id = current_user.get("user_id")
    logger.info(f"Received stats request from user: {user_id or 'global'}")
    
    try:
        # If global key, show all stats; otherwise filter by user
        stats = fetch_threat_stats(user_id=user_id if not current_user.get("is_global") else None)
        return stats
    except Exception as e:
        logger.error(f"Failed to fetch stats: {e}")
        # Return empty stats on error
        return {
            "total": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "actors": 0,
            "last": None
        }
