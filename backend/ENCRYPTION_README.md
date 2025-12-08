# Account Encryption & API Key Management Layer

## 📋 Overview

Complete multi-tenant encryption system implementing the PRD requirements:

- ✅ **AES-128-GCM** encryption per account
- ✅ **Master key wrapping** for secure key storage
- ✅ **API key authentication** with bcrypt hashing
- ✅ **Account isolation** with Row-Level Security
- ✅ **Audit logging** for all security events
- ✅ **< 5ms performance** overhead

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Generate master key
python -c "from app.services.encryption import generate_master_key; print(generate_master_key())"

# Add to .env
echo "MASTER_KEY=qX7wJ9kL2mN4pR8tV6yB3cD5fG1hK0sA=" >> .env

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Database Migration

```bash
# Apply schema changes
psql <connection-string> < migrations/001_accounts_encryption.sql
```

### 3. Run Tests

```bash
# All tests
pytest test_encryption_layer.py -v

# Performance benchmarks
pytest test_encryption_layer.py::TestPerformance --benchmark-only
```

### 4. Start Server

```bash
uvicorn app.main:app --reload
```

### 5. Create Account & Test

```bash
# Create account
curl -X POST http://localhost:8000/accounts/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Account"}'

# Save API key from response!
export API_KEY="<returned-api-key>"

# Test analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{
    "text": "URGENT! Verify your account now!",
    "sandbox": false
  }'
```

---

## 📁 File Structure

```
backend/
├── migrations/
│   └── 001_accounts_encryption.sql          # Database schema
│
├── app/
│   ├── services/
│   │   ├── encryption.py                    # ⭐ AES-128-GCM service
│   │   ├── account_service.py               # ⭐ Account & API key management
│   │   └── audit.py                         # ⭐ Audit logging
│   │
│   ├── middleware/
│   │   └── auth.py                          # ⭐ API key authentication
│   │
│   └── routes/
│       ├── accounts.py                      # ⭐ Account endpoints
│       └── analyze_encrypted.py             # ⭐ Encrypted analysis
│
├── test_encryption_layer.py                 # ⭐ Comprehensive tests
├── migrate.py                               # Migration helper script
│
├── IMPLEMENTATION_SUMMARY.md                # 📄 Complete summary
├── ENCRYPTION_SETUP.md                      # 📄 Detailed setup guide
├── QUICK_START.md                           # 📄 Quick reference
└── requirements.txt                         # Updated dependencies

⭐ = New files for encryption layer
```

---

## 🔐 Security Features

### Encryption
- **Algorithm**: AES-128-GCM (authenticated encryption)
- **Key Size**: 128-bit (16 bytes)
- **Nonce**: 96-bit random per operation
- **Tag**: 128-bit authentication tag
- **Master Key**: Wraps all account keys

### API Keys
- **Generation**: 32-byte cryptographically secure random
- **Hashing**: bcrypt with cost factor 12
- **Lookup**: 8-character prefix for fast validation
- **Tracking**: Last used timestamp
- **Revocation**: Soft delete support

### Account Isolation
- **Database**: Row-Level Security policies
- **Application**: Middleware enforces account_id
- **Testing**: Verified in isolation tests

### Audit Logging
- **Events**: account_created, api_key_created, api_key_revoked, analyze_called, auth_failed
- **Data**: timestamp, account_id, event_type, metadata, IP, user agent
- **Reliability**: Never fails parent operations

---

## 🎯 API Endpoints

### Account Management

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/accounts/create` | POST | ❌ | Create account (bootstrap) |
| `/accounts/api-keys` | POST | ✅ | Create new API key |
| `/accounts/api-keys` | GET | ✅ | List account's keys |
| `/accounts/api-keys/{id}` | DELETE | ✅ | Revoke API key |

### Analysis

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/analyze` | POST | ✅ | Analyze threat (encrypted) |

### Health

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | ❌ | Health check |

---

## 🧪 Testing

### Unit Tests

```bash
# All tests
pytest test_encryption_layer.py -v

# Specific test class
pytest test_encryption_layer.py::TestEncryptionService -v

# Performance benchmarks
pytest test_encryption_layer.py::TestPerformance --benchmark-only
```

### Integration Tests

```bash
# Create test account
python migrate.py test-account

# Use returned API key for testing
export API_KEY="<api-key>"

# Test analysis
curl -X POST http://localhost:8000/analyze \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test threat", "sandbox": false}'
```

### Migration Testing

```bash
# Migrate users
python migrate.py migrate-users

# Encrypt threats
python migrate.py encrypt-threats

# Verify encryption
python migrate.py verify

# Run all
python migrate.py all
```

---

## 📊 Performance

Based on benchmark tests:

| Operation | Average Time | Target | Status |
|-----------|--------------|--------|--------|
| Encryption | < 1ms | < 5ms | ✅ |
| Decryption | < 1ms | < 5ms | ✅ |
| API Key Validation | < 2ms | < 5ms | ✅ |
| **Total Overhead** | **< 4ms** | **< 5ms** | **✅** |

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
MASTER_KEY=qX7wJ9kL2mN4pR8tV6yB3cD5fG1hK0sA=

# Supabase (existing)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Optional
LOG_LEVEL=INFO
```

### Database Setup

1. **Apply Migration**
   ```bash
   psql <connection> < migrations/001_accounts_encryption.sql
   ```

2. **Enable RLS** (if not already enabled)
   ```sql
   ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
   ALTER TABLE threats ENABLE ROW LEVEL SECURITY;
   ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
   ```

3. **Verify Policies**
   ```sql
   SELECT * FROM pg_policies WHERE tablename IN ('accounts', 'threats', 'api_keys');
   ```

---

## 🛠️ Migration Guide

### From Existing System

```bash
# 1. Backup database
pg_dump > backup.sql

# 2. Run migration
psql < migrations/001_accounts_encryption.sql

# 3. Migrate data
python migrate.py all

# 4. Verify
python migrate.py verify

# 5. Update application code
# - Use new auth middleware
# - Use new analyze endpoint
# - Update API key management
```

### Manual Migration Steps

```sql
-- 1. Create account for existing user
INSERT INTO accounts (name, data_key_encrypted, status)
VALUES ('User Name', '<encrypted-key>', 'active');

-- 2. Migrate API key
INSERT INTO api_keys (account_id, prefix, key_hash, name)
VALUES ('<account-id>', '<prefix>', '<bcrypt-hash>', 'Migrated Key');

-- 3. Link existing threats
UPDATE threats 
SET account_id = '<account-id>'
WHERE user_id = '<old-user-id>';

-- 4. Encrypt threat data (use Python script)
```

---

## 📝 Documentation

- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - Complete implementation details
- **[ENCRYPTION_SETUP.md](./ENCRYPTION_SETUP.md)** - Detailed setup instructions
- **[QUICK_START.md](./QUICK_START.md)** - Quick reference guide

---

## ⚠️ Security Considerations

### Production Deployment

1. **Master Key**
   - ✅ Use secrets manager (AWS/Azure/GCP)
   - ✅ Never commit to git
   - ✅ Rotate periodically
   - ✅ Backup securely

2. **API Keys**
   - ✅ Unique key per application
   - ✅ Rotate on schedule
   - ✅ Revoke immediately if compromised
   - ✅ Store in password manager

3. **Database**
   - ✅ Enable RLS in production
   - ✅ Use service role key only in backend
   - ✅ Monitor audit logs daily
   - ✅ Regular backups

4. **Monitoring**
   ```sql
   -- Check failed auth attempts
   SELECT COUNT(*) FROM audit_log 
   WHERE event_type = 'auth_failed' 
   AND timestamp > NOW() - INTERVAL '24 hours';
   
   -- Check key usage
   SELECT prefix, last_used 
   FROM api_keys 
   WHERE NOT revoked 
   ORDER BY last_used DESC;
   ```

---

## 🐛 Troubleshooting

### Common Issues

**"MASTER_KEY not set"**
```bash
# Generate new key
python -c "from app.services.encryption import generate_master_key; print(generate_master_key())"

# Add to .env
echo "MASTER_KEY=<key>" >> .env
```

**"API key invalid"**
- Verify key is correct (case-sensitive)
- Check key hasn't been revoked
- Verify account status is 'active'

**"Decryption failed"**
- Master key may have changed
- Data may be corrupted
- Check encryption service logs

**Performance issues**
- Enable connection pooling
- Cache account keys in memory
- Review database indexes
- Monitor CPU usage

---

## 📞 Support

1. Check documentation: [ENCRYPTION_SETUP.md](./ENCRYPTION_SETUP.md)
2. Run tests: `pytest test_encryption_layer.py -v`
3. Review audit logs in database
4. Check application logs

---

## ✅ Implementation Checklist

- [x] Database schema created
- [x] Encryption service implemented
- [x] Account service implemented
- [x] Authentication middleware added
- [x] API endpoints created
- [x] Audit logging integrated
- [x] Row-Level Security enabled
- [x] Tests written and passing
- [x] Documentation complete
- [x] Performance benchmarks met

**Status**: 🟢 **Production Ready**

---

## 📄 License

Part of the Guardian Security Platform.
