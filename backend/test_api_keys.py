"""Test API key functionality end-to-end"""
import sys
sys.path.insert(0, 'c:/workspace/backend')

from app.services.supabase_client import (
    generate_api_key, 
    create_api_key, 
    list_user_api_keys, 
    verify_api_key,
    deactivate_api_key
)

print("=" * 80)
print("API KEY SYSTEM TEST")
print("=" * 80)
print()

# Test 1: Generate API key format
print("TEST 1: API Key Generation")
print("-" * 40)
key1 = generate_api_key()
key2 = generate_api_key()
print(f"Key 1: {key1[:20]}... (length: {len(key1)})")
print(f"Key 2: {key2[:20]}... (length: {len(key2)})")
print(f"✓ Keys are unique: {key1 != key2}")
print(f"✓ Keys start with 'gsp_': {key1.startswith('gsp_')}")
print()

# Test 2: Create API key for a test user
print("TEST 2: Create API Key")
print("-" * 40)
test_user_id = "test-user-123"  # Mock user ID
try:
    new_key = create_api_key(test_user_id, "Test Key 1")
    print(f"✓ Created key: {new_key['api_key'][:20]}...")
    print(f"  - ID: {new_key['id']}")
    print(f"  - Name: {new_key['name']}")
    print(f"  - Active: {new_key['is_active']}")
    print(f"  - User ID: {new_key['user_id']}")
    created_key_value = new_key['api_key']
    created_key_id = new_key['id']
except Exception as e:
    print(f"✗ Failed to create key: {e}")
    created_key_value = None
    created_key_id = None
print()

# Test 3: Verify the created key
if created_key_value:
    print("TEST 3: Verify API Key")
    print("-" * 40)
    try:
        verified = verify_api_key(created_key_value)
        if verified:
            print(f"✓ Key verified successfully")
            print(f"  - User ID: {verified['user_id']}")
            print(f"  - Key ID: {verified['id']}")
            print(f"  - Name: {verified['name']}")
        else:
            print(f"✗ Key verification returned None")
    except Exception as e:
        print(f"✗ Verification failed: {e}")
    print()

# Test 4: List keys for user
print("TEST 4: List User API Keys")
print("-" * 40)
try:
    keys = list_user_api_keys(test_user_id)
    print(f"✓ Found {len(keys)} key(s) for user {test_user_id}")
    for key in keys:
        print(f"  - {key['name']}: Active={key['is_active']}, ID={key['id']}")
except Exception as e:
    print(f"✗ Failed to list keys: {e}")
print()

# Test 5: Create multiple keys
print("TEST 5: Create Multiple Keys")
print("-" * 40)
try:
    key2 = create_api_key(test_user_id, "Test Key 2")
    key3 = create_api_key(test_user_id, "Test Key 3")
    print(f"✓ Created additional keys")
    
    keys = list_user_api_keys(test_user_id)
    print(f"✓ User now has {len(keys)} total keys")
    for key in keys:
        print(f"  - {key['name']}: Active={key['is_active']}")
except Exception as e:
    print(f"✗ Failed: {e}")
print()

# Test 6: Deactivate a key
if created_key_id:
    print("TEST 6: Deactivate API Key")
    print("-" * 40)
    try:
        deactivate_api_key(created_key_id, test_user_id)
        print(f"✓ Deactivated key {created_key_id}")
        
        # Verify it's deactivated
        keys = list_user_api_keys(test_user_id)
        deactivated = next((k for k in keys if k['id'] == created_key_id), None)
        if deactivated:
            print(f"  - is_active: {deactivated['is_active']}")
            print(f"  ✓ Key properly deactivated" if not deactivated['is_active'] else "  ✗ Key still active")
    except Exception as e:
        print(f"✗ Failed to deactivate: {e}")
    print()

# Test 7: Verify deactivated key doesn't work
if created_key_value:
    print("TEST 7: Verify Deactivated Key Rejected")
    print("-" * 40)
    try:
        verified = verify_api_key(created_key_value)
        if verified is None:
            print(f"✓ Deactivated key correctly rejected")
        else:
            print(f"✗ Deactivated key still validates!")
    except Exception as e:
        print(f"✗ Verification check failed: {e}")
    print()

# Test 8: Auth flow simulation
print("TEST 8: Authentication Flow Simulation")
print("-" * 40)
print("Scenario: User creates first API key")
print("  1. User logs in with Supabase (gets JWT token)")
print("  2. Frontend sends Authorization: Bearer <token>")
print("  3. Backend verifies token → returns user_id")
print("  4. User creates API key via POST /keys")
print("  5. Backend stores key with user_id")
print("  6. Frontend saves key to localStorage")
print("  7. Future requests use x-api-key header")
print()
print("Scenario: User creates additional keys")
print("  1. User already has API key in localStorage")
print("  2. Frontend sends x-api-key header")
print("  3. Backend verifies key → returns user_id")
print("  4. User creates additional key via POST /keys")
print("  5. Frontend does NOT overwrite localStorage")
print("  6. User manually switches keys when needed")
print()

print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print()
print("If you see errors above, check:")
print("  1. Supabase connection (SUPABASE_URL, SUPABASE_SERVICE_KEY)")
print("  2. Database table 'user_api_keys' exists with correct schema")
print("  3. RLS policies allow service role to access the table")
print()
