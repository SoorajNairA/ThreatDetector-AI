"""Supabase client for database operations"""
from typing import Dict, Any, Optional, List, cast
import secrets
from supabase.client import create_client, Client
from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)

# Initialize Supabase client
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY
)


def generate_api_key() -> str:
    """
    Generate a secure random API key.
    
    Returns:
        Secure random API key string
    """
    return f"gsp_{secrets.token_urlsafe(32)}"


def insert_threat(threat_data: Dict[str, Any]) -> None:
    """
    Insert a threat record into the Supabase threats table.
    
    Args:
        threat_data: Dictionary containing threat information
        
    Raises:
        Exception: If insert operation fails
    """
    try:
        logger.info("Inserting threat record into Supabase")
        
        result = supabase.table(settings.SUPABASE_THREATS_TABLE).insert(threat_data).execute()
        
        logger.info(f"Successfully inserted threat record: {result.data}")
    except Exception as e:
        logger.error(f"Failed to insert threat record: {e}")
        raise


def fetch_threat_stats(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch aggregate statistics from the threats table.
    
    Args:
        user_id: Optional user ID to filter stats for specific user
    
    Returns:
        Dictionary containing threat statistics:
        - total: Total number of threats
        - high: Count of HIGH risk threats
        - medium: Count of MEDIUM risk threats
        - low: Count of LOW risk threats
        - actors: Count of unique actors (if available)
        - last: Timestamp of most recent threat (if available)
    """
    try:
        logger.info(f"Fetching threat statistics from Supabase for user: {user_id or 'all'}")
        
        # Build query
        query = supabase.table(settings.SUPABASE_THREATS_TABLE).select("risk_level, actor, timestamp, user_id")
        
        # Filter by user if provided
        if user_id:
            query = query.eq("user_id", user_id)
        
        response = query.execute()
        threats = cast(List[Dict[str, Any]], response.data)
        
        if not threats:
            return {
                "total": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "actors": 0,
                "last": None
            }
        
        # Compute statistics
        total = len(threats)
        high = sum(1 for t in threats if isinstance(t, dict) and t.get("risk_level") == "HIGH")
        medium = sum(1 for t in threats if isinstance(t, dict) and t.get("risk_level") == "MEDIUM")
        low = sum(1 for t in threats if isinstance(t, dict) and t.get("risk_level") == "LOW")
        
        # Get unique actors (handle None values)
        actors = set()
        for t in threats:
            if isinstance(t, dict):
                actor = t.get("actor")
                if actor:
                    actors.add(str(actor))
        unique_actors = len(actors)
        
        # Get most recent timestamp
        timestamps = [str(t.get("timestamp")) for t in threats if isinstance(t, dict) and t.get("timestamp")]
        last_timestamp = max(timestamps) if timestamps else None
        
        stats = {
            "total": total,
            "high": high,
            "medium": medium,
            "low": low,
            "actors": unique_actors,
            "last": last_timestamp
        }
        
        logger.info(f"Statistics: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to fetch threat statistics: {e}")
        raise


def verify_supabase_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Supabase Auth JWT token and return user information.
    
    Args:
        token: JWT token from Supabase Auth
        
    Returns:
        Dictionary with user_id and email if valid, None if invalid
    """
    try:
        # Use Supabase client to verify the token
        response = supabase.auth.get_user(token)
        
        if response and response.user:
            user = response.user
            logger.info(f"Valid Supabase token for user: {user.id}")
            return {
                "user_id": user.id,
                "email": user.email
            }
        
        logger.warning("Invalid Supabase token")
        return None
        
    except Exception as e:
        logger.error(f"Error verifying Supabase token: {e}")
        return None


def verify_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """
    Verify API key and return associated user information.
    
    Args:
        api_key: API key to verify
        
    Returns:
        Dictionary with user_id and key info if valid, None if invalid
    """
    try:
        if not api_key or not api_key.strip():
            logger.warning("Empty API key provided for verification")
            return None
        
        response = supabase.table("user_api_keys").select("*").eq("api_key", api_key).eq("is_active", True).execute()
        
        if not response.data or len(response.data) == 0:
            logger.warning(f"Invalid or inactive API key attempted: {api_key[:10]}...")
            return None
        
        key_data = cast(Dict[str, Any], response.data[0])
        
        # Update last_used_at
        try:
            supabase.table("user_api_keys").update({
                "last_used_at": "now()"
            }).eq("id", key_data["id"]).execute()
        except Exception as update_error:
            # Don't fail authentication if last_used_at update fails
            logger.warning(f"Failed to update last_used_at: {update_error}")
        
        logger.info(f"Valid API key for user: {key_data['user_id']}")
        return key_data
        
    except Exception as e:
        logger.error(f"Error verifying API key: {e}")
        return None


def create_api_key(user_id: str, name: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new API key for a user.
    
    Args:
        user_id: User ID from Supabase Auth (must be valid UUID)
        name: Optional name for the API key
        
    Returns:
        Dictionary with api_key and metadata
    """
    try:
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")
        
        api_key = generate_api_key()
        
        data = {
            "user_id": user_id,
            "api_key": api_key,
            "name": name or "Default Key",
            "is_active": True
        }
        
        logger.info(f"Creating API key for user: {user_id}, name: {name}")
        response = supabase.table("user_api_keys").insert(data).execute()
        
        if not response.data or len(response.data) == 0:
            raise Exception("Insert returned no data")
        
        logger.info(f"Successfully created API key for user: {user_id}")
        return cast(Dict[str, Any], response.data[0])
        
    except Exception as e:
        logger.error(f"Failed to create API key for user {user_id}: {e}")
        raise


def list_user_api_keys(user_id: str) -> list:
    """
    List all API keys for a user.
    
    Args:
        user_id: User ID from Supabase Auth
        
    Returns:
        List of API key records
    """
    try:
        response = supabase.table("user_api_keys").select("id, name, is_active, created_at, last_used_at").eq("user_id", user_id).execute()
        
        return cast(List[Dict[str, Any]], response.data)
        
    except Exception as e:
        logger.error(f"Failed to list API keys: {e}")
        raise


def deactivate_api_key(key_id: str, user_id: str) -> bool:
    """
    Deactivate an API key.
    
    Args:
        key_id: API key ID to deactivate
        user_id: User ID (for authorization)
        
    Returns:
        True if successful
    """
    try:
        response = supabase.table("user_api_keys").update({
            "is_active": False
        }).eq("id", key_id).eq("user_id", user_id).execute()
        
        logger.info(f"Deactivated API key: {key_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to deactivate API key: {e}")
        raise
