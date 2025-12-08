"""
API Key Management Service
Handles account creation, API key generation, hashing, and validation
"""
import secrets
import hashlib
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timezone
import bcrypt
from app.services.supabase_client import supabase
from app.services.encryption import get_encryption_service
from app.logging_config import get_logger

logger = get_logger(__name__)


class AccountService:
    """Manages accounts and API keys"""
    
    def __init__(self):
        self.supabase = supabase
        self.encryption = get_encryption_service()
    
    # ========================================================================
    # ACCOUNT MANAGEMENT
    # ========================================================================
    
    def create_account(self, name: str) -> Dict[str, Any]:
        """
        Create a new account with encrypted data key
        
        Args:
            name: Account display name
            
        Returns:
            Account record with id
        """
        # Generate per-account encryption key
        account_key = self.encryption.generate_account_key()
        
        # Wrap with master key
        ciphertext, nonce, tag = self.encryption.wrap_account_key(account_key)
        
        # Combine for storage (format: nonce:tag:ciphertext)
        data_key_encrypted = f"{nonce}:{tag}:{ciphertext}"
        
        # Insert account
        result = self.supabase.table("accounts").insert({
            "name": name,
            "data_key_encrypted": data_key_encrypted,
            "status": "active"
        }).execute()
        
        if not result.data:
            raise Exception("Failed to create account")
        
        account = result.data[0]
        logger.info(f"Created account: {account['id']}")
        
        return account
    
    def get_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """
        Get account by ID
        
        Args:
            account_id: Account UUID
            
        Returns:
            Account record or None
        """
        result = self.supabase.table("accounts").select("*").eq("id", account_id).execute()
        
        if result.data:
            return result.data[0]
        return None
    
    def get_account_key(self, account_id: str) -> bytes:
        """
        Get decrypted account encryption key
        
        Args:
            account_id: Account UUID
            
        Returns:
            16-byte decrypted account key
            
        Raises:
            ValueError: If account not found or decryption fails
        """
        account = self.get_account(account_id)
        if not account:
            raise ValueError(f"Account not found: {account_id}")
        
        # Parse stored format: nonce:tag:ciphertext
        parts = account["data_key_encrypted"].split(":")
        if len(parts) != 3:
            raise ValueError("Invalid encrypted key format")
        
        nonce, tag, ciphertext = parts
        
        # Unwrap account key
        account_key = self.encryption.unwrap_account_key(ciphertext, nonce, tag)
        
        return account_key
    
    # ========================================================================
    # API KEY MANAGEMENT
    # ========================================================================
    
    def generate_api_key(self, account_id: str, name: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a new API key for an account
        
        Args:
            account_id: Account UUID
            name: Optional friendly name for the key
            
        Returns:
            Tuple of (plaintext_key, key_record)
            Plaintext key is only returned once!
        """
        # Generate random API key (32 bytes = 256 bits)
        key_bytes = secrets.token_bytes(32)
        plaintext_key = base64_url_encode(key_bytes)
        
        # Create prefix (first 8 chars)
        prefix = plaintext_key[:8]
        
        # Hash the full key with bcrypt
        key_hash = bcrypt.hashpw(plaintext_key.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert API key record
        result = self.supabase.table("api_keys").insert({
            "account_id": account_id,
            "prefix": prefix,
            "key_hash": key_hash,
            "name": name,
            "revoked": False
        }).execute()
        
        if not result.data:
            raise Exception("Failed to create API key")
        
        key_record = result.data[0]
        logger.info(f"Created API key {key_record['id']} for account {account_id}")
        
        # Return plaintext key (only time it's available!)
        return plaintext_key, key_record
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key and return account info
        
        Args:
            api_key: Plaintext API key from request
            
        Returns:
            Dict with account_id and key_id if valid, None otherwise
        """
        if not api_key or len(api_key) < 8:
            return None
        
        # Extract prefix
        prefix = api_key[:8]
        
        # Look up by prefix
        result = self.supabase.table("api_keys").select(
            "id, account_id, key_hash, revoked, account:accounts(status)"
        ).eq("prefix", prefix).eq("revoked", False).execute()
        
        if not result.data:
            logger.warning(f"No API key found with prefix: {prefix}")
            return None
        
        key_record = result.data[0]
        
        # Check if account is active
        account = key_record.get("account")
        if not account or account.get("status") != "active":
            logger.warning(f"Account suspended for key: {key_record['id']}")
            return None
        
        # Verify hash
        key_hash = key_record["key_hash"].encode('utf-8')
        if not bcrypt.checkpw(api_key.encode('utf-8'), key_hash):
            logger.warning(f"Invalid API key hash for prefix: {prefix}")
            return None
        
        # Update last_used timestamp
        self.supabase.table("api_keys").update({
            "last_used": datetime.now(timezone.utc).isoformat()
        }).eq("id", key_record["id"]).execute()
        
        logger.info(f"Validated API key {key_record['id']} for account {key_record['account_id']}")
        
        return {
            "account_id": key_record["account_id"],
            "key_id": key_record["id"]
        }
    
    def revoke_api_key(self, key_id: str, account_id: str) -> bool:
        """
        Revoke an API key
        
        Args:
            key_id: API key UUID
            account_id: Account UUID (for authorization)
            
        Returns:
            True if revoked successfully
        """
        result = self.supabase.table("api_keys").update({
            "revoked": True,
            "revoked_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", key_id).eq("account_id", account_id).execute()
        
        if result.data:
            logger.info(f"Revoked API key {key_id}")
            return True
        
        return False
    
    def list_api_keys(self, account_id: str) -> List[Dict[str, Any]]:
        """
        List all API keys for an account
        
        Args:
            account_id: Account UUID
            
        Returns:
            List of API key records (without hashes)
        """
        result = self.supabase.table("api_keys").select(
            "id, prefix, name, created_at, last_used, revoked, revoked_at"
        ).eq("account_id", account_id).order("created_at", desc=True).execute()
        
        return result.data if result.data else []


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def base64_url_encode(data: bytes) -> str:
    """
    URL-safe base64 encoding without padding
    
    Args:
        data: Bytes to encode
        
    Returns:
        URL-safe base64 string
    """
    import base64
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')


def base64_url_decode(data: str) -> bytes:
    """
    Decode URL-safe base64 string
    
    Args:
        data: URL-safe base64 string
        
    Returns:
        Decoded bytes
    """
    import base64
    # Add padding if needed
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)


# Singleton instance
_account_service: Optional[AccountService] = None


def get_account_service() -> AccountService:
    """
    Get or create account service singleton
    
    Returns:
        AccountService instance
    """
    global _account_service
    if _account_service is None:
        _account_service = AccountService()
    return _account_service
