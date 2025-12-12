"""
Encryption Service - AES-128-GCM
Handles per-account key encryption and data encryption
"""
import os
import base64
import secrets
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.logging_config import get_logger

logger = get_logger(__name__)


class EncryptionService:
    """
    Handles AES-128-GCM encryption and decryption
    - Master key wrapping/unwrapping
    - Per-account data encryption
    """
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize encryption service
        
        Args:
            master_key: 16-byte master key for wrapping account keys
                       If None, loads from MASTER_KEY environment variable
        """
        if master_key is None:
            master_key_b64 = os.getenv("MASTER_KEY")
            if not master_key_b64:
                raise ValueError("MASTER_KEY environment variable not set")
            try:
                master_key = base64.b64decode(master_key_b64)
            except Exception as e:
                raise ValueError(f"Invalid MASTER_KEY format: {e}")
        
        if len(master_key) != 16:
            raise ValueError(f"Master key must be 16 bytes (128 bits), got {len(master_key)}")
        
        self.master_key = master_key
        self.master_cipher = AESGCM(master_key)
        logger.info("Encryption service initialized")
    
    # ========================================================================
    # ACCOUNT KEY MANAGEMENT
    # ========================================================================
    
    def generate_account_key(self) -> bytes:
        """
        Generate a random 16-byte (128-bit) account key
        
        Returns:
            Random 16-byte key
        """
        return secrets.token_bytes(16)
    
    def wrap_account_key(self, account_key: bytes) -> Tuple[str, str, str]:
        """
        Encrypt (wrap) an account key with the master key
        
        Args:
            account_key: 16-byte account key to wrap
            
        Returns:
            Tuple of (ciphertext_b64, nonce_b64, tag_b64)
        """
        if len(account_key) != 16:
            raise ValueError(f"Account key must be 16 bytes, got {len(account_key)}")
        
        # Generate random nonce (96 bits recommended for GCM)
        nonce = secrets.token_bytes(12)
        
        # Encrypt account key with master key
        # GCM returns ciphertext with authentication tag appended
        ciphertext_with_tag = self.master_cipher.encrypt(nonce, account_key, None)
        
        # Split ciphertext and tag (tag is last 16 bytes)
        ciphertext = ciphertext_with_tag[:-16]
        tag = ciphertext_with_tag[-16:]
        
        # Return base64 encoded values
        return (
            base64.b64encode(ciphertext).decode('utf-8'),
            base64.b64encode(nonce).decode('utf-8'),
            base64.b64encode(tag).decode('utf-8')
        )
    
    def unwrap_account_key(self, ciphertext_b64: str, nonce_b64: str, tag_b64: str) -> bytes:
        """
        Decrypt (unwrap) an account key using the master key
        
        Args:
            ciphertext_b64: Base64 encoded ciphertext
            nonce_b64: Base64 encoded nonce
            tag_b64: Base64 encoded authentication tag
            
        Returns:
            Decrypted 16-byte account key
            
        Raises:
            ValueError: If decryption fails (wrong key, corrupted data)
        """
        try:
            ciphertext = base64.b64decode(ciphertext_b64)
            nonce = base64.b64decode(nonce_b64)
            tag = base64.b64decode(tag_b64)
            
            # Combine ciphertext and tag for GCM
            ciphertext_with_tag = ciphertext + tag
            
            # Decrypt
            account_key = self.master_cipher.decrypt(nonce, ciphertext_with_tag, None)
            
            if len(account_key) != 16:
                raise ValueError(f"Unwrapped key has wrong length: {len(account_key)}")
            
            return account_key
            
        except Exception as e:
            logger.error(f"Failed to unwrap account key: {e}")
            raise ValueError("Decryption failed")
    
    # ========================================================================
    # DATA ENCRYPTION (using account key)
    # ========================================================================
    
    def encrypt_data(self, account_key: bytes, plaintext: str) -> Tuple[str, str, str]:
        """
        Encrypt data using an account key
        
        Args:
            account_key: 16-byte account encryption key
            plaintext: String data to encrypt
            
        Returns:
            Tuple of (ciphertext_b64, nonce_b64, tag_b64)
        """
        if len(account_key) != 16:
            raise ValueError(f"Account key must be 16 bytes, got {len(account_key)}")
        
        # Create cipher with account key
        cipher = AESGCM(account_key)
        
        # Generate random nonce
        nonce = secrets.token_bytes(12)
        
        # Convert plaintext to bytes
        plaintext_bytes = plaintext.encode('utf-8')
        
        # Encrypt
        ciphertext_with_tag = cipher.encrypt(nonce, plaintext_bytes, None)
        
        # Split ciphertext and tag
        ciphertext = ciphertext_with_tag[:-16]
        tag = ciphertext_with_tag[-16:]
        
        return (
            base64.b64encode(ciphertext).decode('utf-8'),
            base64.b64encode(nonce).decode('utf-8'),
            base64.b64encode(tag).decode('utf-8')
        )
    
    def decrypt_data(self, account_key: bytes, ciphertext_b64: str, 
                     nonce_b64: str, tag_b64: str) -> str:
        """
        Decrypt data using an account key
        
        Args:
            account_key: 16-byte account encryption key
            ciphertext_b64: Base64 encoded ciphertext
            nonce_b64: Base64 encoded nonce
            tag_b64: Base64 encoded authentication tag
            
        Returns:
            Decrypted plaintext string
            
        Raises:
            ValueError: If decryption fails
        """
        if len(account_key) != 16:
            raise ValueError(f"Account key must be 16 bytes, got {len(account_key)}")
        
        try:
            # Decode base64
            ciphertext = base64.b64decode(ciphertext_b64)
            nonce = base64.b64decode(nonce_b64)
            tag = base64.b64decode(tag_b64)
            
            # Create cipher
            cipher = AESGCM(account_key)
            
            # Combine ciphertext and tag
            ciphertext_with_tag = ciphertext + tag
            
            # Decrypt
            plaintext_bytes = cipher.decrypt(nonce, ciphertext_with_tag, None)
            
            return plaintext_bytes.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise ValueError("Decryption failed")


# ============================================================================
# KEY GENERATION UTILITY
# ============================================================================

def generate_master_key() -> str:
    """
    Generate a new master key for first-time setup
    
    Returns:
        Base64 encoded 16-byte key
    """
    master_key = secrets.token_bytes(16)
    return base64.b64encode(master_key).decode('utf-8')


# Singleton instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """
    Get or create encryption service singleton
    
    Returns:
        EncryptionService instance
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


if __name__ == "__main__":
    # Generate a new master key for setup
    print("Generated Master Key (save to .env as MASTER_KEY):")
    print(generate_master_key())
