"""
Tests for Encryption and Account Management
Run with: pytest test_encryption_layer.py -v
"""
import pytest
import secrets
import base64
from app.services.encryption import EncryptionService, generate_master_key


class TestEncryptionService:
    """Test encryption service functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        # Generate test master key
        self.master_key = secrets.token_bytes(16)
        self.encryption = EncryptionService(self.master_key)
    
    def test_generate_account_key(self):
        """Test account key generation"""
        key = self.encryption.generate_account_key()
        assert len(key) == 16
        assert isinstance(key, bytes)
    
    def test_wrap_unwrap_account_key(self):
        """Test key wrapping round trip"""
        # Generate account key
        account_key = self.encryption.generate_account_key()
        
        # Wrap it
        ciphertext, nonce, tag = self.encryption.wrap_account_key(account_key)
        
        # Verify base64 encoding
        assert isinstance(ciphertext, str)
        assert isinstance(nonce, str)
        assert isinstance(tag, str)
        
        # Unwrap it
        unwrapped_key = self.encryption.unwrap_account_key(ciphertext, nonce, tag)
        
        # Should match original
        assert unwrapped_key == account_key
    
    def test_unwrap_with_wrong_key_fails(self):
        """Test that unwrapping with wrong master key fails"""
        # Generate and wrap with first master key
        account_key = self.encryption.generate_account_key()
        ciphertext, nonce, tag = self.encryption.wrap_account_key(account_key)
        
        # Try to unwrap with different master key
        wrong_master_key = secrets.token_bytes(16)
        wrong_encryption = EncryptionService(wrong_master_key)
        
        with pytest.raises(ValueError, match="Decryption failed"):
            wrong_encryption.unwrap_account_key(ciphertext, nonce, tag)
    
    def test_encrypt_decrypt_data(self):
        """Test data encryption round trip"""
        # Generate account key
        account_key = self.encryption.generate_account_key()
        
        # Test data
        plaintext = "This is sensitive threat data!"
        
        # Encrypt
        ciphertext, nonce, tag = self.encryption.encrypt_data(account_key, plaintext)
        
        # Verify base64 encoding
        assert isinstance(ciphertext, str)
        assert isinstance(nonce, str)
        assert isinstance(tag, str)
        
        # Decrypt
        decrypted = self.encryption.decrypt_data(account_key, ciphertext, nonce, tag)
        
        # Should match original
        assert decrypted == plaintext
    
    def test_decrypt_with_wrong_key_fails(self):
        """Test that decryption with wrong account key fails"""
        # Encrypt with one key
        account_key1 = self.encryption.generate_account_key()
        plaintext = "Secret message"
        ciphertext, nonce, tag = self.encryption.encrypt_data(account_key1, plaintext)
        
        # Try to decrypt with different key
        account_key2 = self.encryption.generate_account_key()
        
        with pytest.raises(ValueError, match="Decryption failed"):
            self.encryption.decrypt_data(account_key2, ciphertext, nonce, tag)
    
    def test_encrypt_unicode_data(self):
        """Test encryption of unicode characters"""
        account_key = self.encryption.generate_account_key()
        
        # Unicode test data
        plaintext = "Hello 世界! 🔐🚀"
        
        # Encrypt and decrypt
        ciphertext, nonce, tag = self.encryption.encrypt_data(account_key, plaintext)
        decrypted = self.encryption.decrypt_data(account_key, ciphertext, nonce, tag)
        
        assert decrypted == plaintext
    
    def test_encrypt_large_data(self):
        """Test encryption of large text"""
        account_key = self.encryption.generate_account_key()
        
        # Large text (10KB)
        plaintext = "A" * 10000
        
        # Encrypt and decrypt
        ciphertext, nonce, tag = self.encryption.encrypt_data(account_key, plaintext)
        decrypted = self.encryption.decrypt_data(account_key, ciphertext, nonce, tag)
        
        assert decrypted == plaintext
        assert len(decrypted) == 10000
    
    def test_master_key_validation(self):
        """Test that invalid master keys are rejected"""
        # Too short
        with pytest.raises(ValueError, match="must be 16 bytes"):
            EncryptionService(b"short")
        
        # Too long
        with pytest.raises(ValueError, match="must be 16 bytes"):
            EncryptionService(secrets.token_bytes(32))
    
    def test_generate_master_key_format(self):
        """Test master key generation utility"""
        master_key_b64 = generate_master_key()
        
        # Should be base64 string
        assert isinstance(master_key_b64, str)
        
        # Should decode to 16 bytes
        decoded = base64.b64decode(master_key_b64)
        assert len(decoded) == 16


class TestAccountIsolation:
    """Test that accounts cannot access each other's data"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.master_key = secrets.token_bytes(16)
        self.encryption = EncryptionService(self.master_key)
        
        # Create two account keys
        self.account_key_a = self.encryption.generate_account_key()
        self.account_key_b = self.encryption.generate_account_key()
    
    def test_account_a_cannot_decrypt_account_b_data(self):
        """Test that account A cannot decrypt account B's data"""
        # Account B encrypts data
        plaintext = "Account B's secret data"
        ciphertext, nonce, tag = self.encryption.encrypt_data(
            self.account_key_b, 
            plaintext
        )
        
        # Account A tries to decrypt with their key
        with pytest.raises(ValueError, match="Decryption failed"):
            self.encryption.decrypt_data(
                self.account_key_a,
                ciphertext,
                nonce,
                tag
            )
    
    def test_same_plaintext_different_ciphertexts(self):
        """Test that same plaintext produces different ciphertexts (due to random nonce)"""
        plaintext = "Test message"
        
        # Encrypt twice with same key
        ct1, n1, t1 = self.encryption.encrypt_data(self.account_key_a, plaintext)
        ct2, n2, t2 = self.encryption.encrypt_data(self.account_key_a, plaintext)
        
        # Ciphertexts should differ (random nonces)
        assert ct1 != ct2
        assert n1 != n2
        
        # But both should decrypt correctly
        dec1 = self.encryption.decrypt_data(self.account_key_a, ct1, n1, t1)
        dec2 = self.encryption.decrypt_data(self.account_key_a, ct2, n2, t2)
        
        assert dec1 == plaintext
        assert dec2 == plaintext


class TestPerformance:
    """Test encryption performance requirements"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.master_key = secrets.token_bytes(16)
        self.encryption = EncryptionService(self.master_key)
        self.account_key = self.encryption.generate_account_key()
    
    def test_encryption_performance(self, benchmark):
        """Test that encryption is fast enough (< 5ms requirement)"""
        plaintext = "Test threat message for performance testing"
        
        # Benchmark encryption
        result = benchmark(
            self.encryption.encrypt_data,
            self.account_key,
            plaintext
        )
        
        # Should complete in < 5ms (5000 microseconds)
        assert benchmark.stats.stats.mean < 0.005  # 5 milliseconds
    
    def test_decryption_performance(self, benchmark):
        """Test that decryption is fast enough"""
        plaintext = "Test threat message for performance testing"
        ciphertext, nonce, tag = self.encryption.encrypt_data(
            self.account_key,
            plaintext
        )
        
        # Benchmark decryption
        result = benchmark(
            self.encryption.decrypt_data,
            self.account_key,
            ciphertext,
            nonce,
            tag
        )
        
        # Should complete in < 5ms (5000 microseconds)
        assert benchmark.stats.stats.mean < 0.005


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
