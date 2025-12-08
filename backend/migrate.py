"""
Migration Helper Script
Helps transition from old system to new encrypted account system
"""
import os
import sys
from typing import List, Dict, Any
from app.services.encryption import get_encryption_service
from app.services.account_service import get_account_service
from app.services.supabase_client import supabase
from app.logging_config import get_logger

logger = get_logger(__name__)


def migrate_users_to_accounts():
    """
    Migrate existing user_api_keys records to accounts + api_keys tables
    
    Creates:
    - One account per unique user_id
    - Migrates existing keys (requires re-hashing)
    """
    account_service = get_account_service()
    
    print("🔄 Migrating users to accounts...")
    
    # Get unique users from old table
    result = supabase.table("user_api_keys").select("user_id, DISTINCT").execute()
    
    if not result.data:
        print("✅ No users to migrate")
        return
    
    unique_users = set(row["user_id"] for row in result.data)
    print(f"Found {len(unique_users)} unique users")
    
    # Create accounts
    for user_id in unique_users:
        try:
            # Check if account already exists
            existing = supabase.table("accounts").select("id").eq("id", user_id).execute()
            
            if existing.data:
                print(f"⏭️  Account {user_id} already exists")
                continue
            
            # Create account with user_id as name
            account = account_service.create_account(f"User {user_id}")
            print(f"✅ Created account: {account['id']}")
            
        except Exception as e:
            print(f"❌ Failed to create account for {user_id}: {e}")
    
    print("✅ User migration complete")


def encrypt_existing_threats():
    """
    Encrypt plaintext threat data with per-account keys
    
    For each threat without encryption:
    1. Get account encryption key
    2. Encrypt text field
    3. Store encrypted values
    4. Clear plaintext (optional)
    """
    encryption_service = get_encryption_service()
    account_service = get_account_service()
    
    print("🔄 Encrypting existing threats...")
    
    # Get threats without encryption
    result = supabase.table("threats").select("*").is_("text_enc", None).execute()
    
    if not result.data:
        print("✅ No threats to encrypt")
        return
    
    print(f"Found {len(result.data)} threats to encrypt")
    
    success_count = 0
    error_count = 0
    
    for threat in result.data:
        try:
            threat_id = threat["id"]
            account_id = threat.get("account_id") or threat.get("user_id")
            
            if not account_id:
                print(f"⚠️  Threat {threat_id} has no account_id")
                error_count += 1
                continue
            
            # Get plaintext
            plaintext = threat.get("text") or threat.get("content")
            
            if not plaintext:
                print(f"⚠️  Threat {threat_id} has no text content")
                error_count += 1
                continue
            
            # Get account key
            account_key = account_service.get_account_key(account_id)
            
            # Encrypt
            text_enc, nonce, tag = encryption_service.encrypt_data(
                account_key,
                plaintext
            )
            
            # Update record
            supabase.table("threats").update({
                "text_enc": text_enc,
                "nonce": nonce,
                "tag": tag,
                "account_id": account_id
                # Optionally: "text": None  # Clear plaintext
            }).eq("id", threat_id).execute()
            
            success_count += 1
            
            if success_count % 100 == 0:
                print(f"  Encrypted {success_count} threats...")
            
        except Exception as e:
            print(f"❌ Failed to encrypt threat {threat_id}: {e}")
            error_count += 1
    
    print(f"✅ Threat encryption complete: {success_count} success, {error_count} errors")


def verify_encryption():
    """
    Verify encrypted data can be decrypted successfully
    """
    encryption_service = get_encryption_service()
    account_service = get_account_service()
    
    print("🔍 Verifying encryption...")
    
    # Get sample encrypted threats
    result = supabase.table("threats").select("*").not_.is_("text_enc", None).limit(10).execute()
    
    if not result.data:
        print("⚠️  No encrypted threats found")
        return
    
    success_count = 0
    error_count = 0
    
    for threat in result.data:
        try:
            account_id = threat["account_id"]
            text_enc = threat["text_enc"]
            nonce = threat["nonce"]
            tag = threat["tag"]
            
            # Get account key
            account_key = account_service.get_account_key(account_id)
            
            # Decrypt
            plaintext = encryption_service.decrypt_data(
                account_key,
                text_enc,
                nonce,
                tag
            )
            
            if plaintext:
                success_count += 1
                print(f"✅ Verified threat {threat['id']} (length: {len(plaintext)})")
            else:
                error_count += 1
                print(f"❌ Empty plaintext for threat {threat['id']}")
            
        except Exception as e:
            error_count += 1
            print(f"❌ Failed to decrypt threat {threat['id']}: {e}")
    
    if error_count == 0:
        print(f"✅ Verification complete: All {success_count} threats decrypted successfully")
    else:
        print(f"⚠️  Verification complete: {success_count} success, {error_count} errors")


def generate_test_account():
    """
    Generate a test account with API key for testing
    """
    account_service = get_account_service()
    
    print("🧪 Creating test account...")
    
    # Create account
    account = account_service.create_account("Test Account")
    print(f"✅ Created account: {account['id']}")
    
    # Generate API key
    api_key, key_record = account_service.generate_api_key(
        account["id"],
        name="Test API Key"
    )
    
    print(f"✅ Generated API key: {api_key}")
    print(f"   Prefix: {key_record['prefix']}")
    print(f"   Key ID: {key_record['id']}")
    print("\n⚠️  Save this API key - it won't be shown again!")
    
    return {
        "account_id": account["id"],
        "api_key": api_key
    }


def main():
    """Main migration script"""
    print("=" * 60)
    print("Account Encryption Migration Helper")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python migrate.py <command>")
        print()
        print("Commands:")
        print("  migrate-users    - Migrate user_api_keys to accounts")
        print("  encrypt-threats  - Encrypt existing threat data")
        print("  verify          - Verify encryption/decryption works")
        print("  test-account    - Create test account with API key")
        print("  all             - Run all migration steps")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Check MASTER_KEY is set
    if not os.getenv("MASTER_KEY"):
        print("❌ ERROR: MASTER_KEY environment variable not set")
        print("Generate one with:")
        print("  python -c \"from app.services.encryption import generate_master_key; print(generate_master_key())\"")
        sys.exit(1)
    
    try:
        if command == "migrate-users":
            migrate_users_to_accounts()
        
        elif command == "encrypt-threats":
            encrypt_existing_threats()
        
        elif command == "verify":
            verify_encryption()
        
        elif command == "test-account":
            generate_test_account()
        
        elif command == "all":
            migrate_users_to_accounts()
            print()
            encrypt_existing_threats()
            print()
            verify_encryption()
            print()
            print("✅ All migration steps complete!")
        
        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
