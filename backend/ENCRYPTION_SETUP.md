# Account Encryption & API Key Management - Setup Guide

## Overview

This implementation adds a complete multi-tenant encryption layer to the threat analysis system. Each account has:

- **Per-account encryption keys** (AES-128-GCM) wrapped with a master key
- **API key authentication** with bcrypt hashing
- **Encrypted threat data** stored in database
- **Row-level security** preventing cross-account data access
- **Audit logging** for all security events

---

## 1. Generate Master Key

The master key is used to encrypt/decrypt per-account keys. Generate it once and store securely:

```bash
cd backend
python -c "from app.services.encryption import generate_master_key; print(generate_master_key())"
```

Example output:
```
qX7wJ9kL2mN4pR8tV6yB3cD5fG1hK0sA=
```

---

## 2. Update Environment Variables

Add to `.env`:

```bash
# Master encryption key (generated above)
MASTER_KEY=qX7wJ9kL2mN4pR8tV6yB3cD5fG1hK0sA=

# Supabase configuration (existing)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
```

**⚠️ CRITICAL**: Never commit `.env` to version control. The master key must be kept secret.

---

## 3. Run Database Migration

Apply the schema changes to Supabase:

```bash
# Connect to your Supabase database
psql postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres

# Run migration
\i migrations/001_accounts_encryption.sql
```

Or use Supabase Dashboard:
1. Go to SQL Editor
2. Copy contents of `migrations/001_accounts_encryption.sql`
3. Execute

This creates:
- `accounts` table
- `api_keys` table
- Updated `threats` table with encryption fields
- `audit_log` table
- Row-level security policies

---

## 4. Install Python Dependencies

```bash
pip install cryptography bcrypt pytest pytest-benchmark
```

Update `requirements.txt`:
```txt
cryptography>=41.0.0
bcrypt>=4.0.0
pytest>=7.4.0
pytest-benchmark>=4.0.0
```

---

## 5. Update FastAPI Application

### 5.1 Update `main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import accounts, analyze_encrypted
from app.middleware.auth import authentication_middleware

app = FastAPI(title="Threat Analysis API")

# Add authentication middleware
app.middleware("http")(authentication_middleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(accounts.router)
app.include_router(analyze_encrypted.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

### 5.2 Replace Old Auth

The old `app/services/auth.py` is replaced by:
- `app/middleware/auth.py` (API key validation)
- `app/services/account_service.py` (account management)

---

## 6. Testing

### 6.1 Run Unit Tests

```bash
pytest test_encryption_layer.py -v
```

Expected output:
```
test_encryption_layer.py::TestEncryptionService::test_generate_account_key PASSED
test_encryption_layer.py::TestEncryptionService::test_wrap_unwrap_account_key PASSED
test_encryption_layer.py::TestEncryptionService::test_encrypt_decrypt_data PASSED
test_encryption_layer.py::TestAccountIsolation::test_account_a_cannot_decrypt_account_b_data PASSED
test_encryption_layer.py::TestPerformance::test_encryption_performance PASSED
```

### 6.2 Integration Test

```bash
# Start server
uvicorn app.main:app --reload

# In another terminal, test the flow:

# 1. Create account
curl -X POST http://localhost:8000/accounts/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Account"}'

# Response includes account_id and first API key:
# {
#   "account_id": "123e4567-e89b-12d3-a456-426614174000",
#   "api_key": "abc123...",
#   "message": "Save your API key..."
# }

# 2. Test analysis with API key
export API_KEY="abc123..."

curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{
    "text": "URGENT! Your account has been compromised.",
    "sandbox": false
  }'

# 3. Create additional API key
curl -X POST http://localhost:8000/accounts/api-keys \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"name": "Production Key"}'

# 4. List API keys
curl -X GET http://localhost:8000/accounts/api-keys \
  -H "x-api-key: $API_KEY"

# 5. Revoke an API key
curl -X DELETE http://localhost:8000/accounts/api-keys/{key_id} \
  -H "x-api-key: $API_KEY"
```

---

## 7. Migration from Existing System

If you have existing data:

### 7.1 Migrate Users to Accounts

```sql
-- Create account for each existing user
INSERT INTO accounts (id, name, data_key_encrypted, status)
SELECT 
    user_id,
    email,
    -- Generate and wrap encryption key (requires backend script)
    'PLACEHOLDER',
    'active'
FROM user_api_keys
GROUP BY user_id, email;
```

### 7.2 Migrate API Keys

```sql
-- Copy existing API keys
INSERT INTO api_keys (id, account_id, prefix, key_hash, created_at, revoked)
SELECT 
    id,
    user_id as account_id,
    LEFT(api_key, 8) as prefix,
    api_key as key_hash,  -- Re-hash these!
    created_at,
    NOT is_active as revoked
FROM user_api_keys;
```

**Note**: Existing keys need to be re-hashed with bcrypt.

### 7.3 Encrypt Existing Threat Data

```python
# Backend migration script
from app.services.encryption import get_encryption_service
from app.services.account_service import get_account_service
from app.services.supabase_client import get_supabase_client

supabase = get_supabase_client()
encryption = get_encryption_service()
account_service = get_account_service()

# Get all threats without encryption
threats = supabase.table("threats").select("*").is_("text_enc", None).execute()

for threat in threats.data:
    account_id = threat["account_id"]  # or user_id
    
    # Get account key
    account_key = account_service.get_account_key(account_id)
    
    # Encrypt text
    text_enc, nonce, tag = encryption.encrypt_data(
        account_key,
        threat["text"]
    )
    
    # Update record
    supabase.table("threats").update({
        "text_enc": text_enc,
        "nonce": nonce,
        "tag": tag,
        "text": None  # Clear plaintext
    }).eq("id", threat["id"]).execute()
```

---

## 8. Security Best Practices

### 8.1 Master Key Rotation

To rotate the master key:

1. Generate new master key
2. For each account:
   - Decrypt account key with old master
   - Re-encrypt with new master
   - Update database
3. Update MASTER_KEY in environment
4. Restart application

### 8.2 API Key Management

- API keys shown **only once** at creation
- Store keys in secure password manager
- Rotate keys periodically
- Revoke unused keys
- Use separate keys for dev/staging/prod

### 8.3 Monitoring

Check audit logs regularly:

```sql
SELECT event_type, COUNT(*) 
FROM audit_log 
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY event_type;
```

---

## 9. API Endpoints Summary

### Account Management

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/accounts/create` | POST | None | Create new account (bootstrap) |
| `/accounts/api-keys` | POST | Required | Create new API key |
| `/accounts/api-keys` | GET | Required | List account's API keys |
| `/accounts/api-keys/{id}` | DELETE | Required | Revoke API key |

### Analysis

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/analyze` | POST | Required | Analyze threat (encrypted storage) |

### Health

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | None | Health check |

---

## 10. Troubleshooting

### Error: "MASTER_KEY environment variable not set"

```bash
# Check .env file exists and has MASTER_KEY
cat .env | grep MASTER_KEY

# If missing, generate new key
python -c "from app.services.encryption import generate_master_key; print(generate_master_key())"
```

### Error: "Invalid or revoked API key"

- Check API key is correct (case-sensitive)
- Verify key hasn't been revoked
- Check account status is 'active'

### Error: "Decryption failed"

- Master key may have changed
- Data may be corrupted
- Check encryption service logs

### Performance Issues

Encryption should be < 5ms per request. If slower:

1. Check CPU usage
2. Review database query performance
3. Enable query caching for account keys
4. Use connection pooling

---

## 11. Architecture Diagram

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ x-api-key header
       ▼
┌─────────────────────┐
│  Authentication     │
│  Middleware         │
│  - Validate key     │
│  - Attach account   │
└──────┬──────────────┘
       │ account_id
       ▼
┌─────────────────────┐
│  /analyze Endpoint  │
│  - Run classifiers  │
│  - Get account key  │
│  - Encrypt data     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Supabase DB       │
│  - threats (enc)    │
│  - accounts         │
│  - api_keys         │
│  - audit_log        │
│  + RLS policies     │
└─────────────────────┘
```

---

## Support

For issues or questions:
1. Check logs: `tail -f logs/app.log`
2. Run tests: `pytest -v`
3. Review audit log in database
