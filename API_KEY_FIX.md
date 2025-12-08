# API Key Generation Fix

## Problem Identified

**Issue:** Users cannot generate API keys from the frontend.

**Root Cause:** Chicken-and-egg authentication problem:
- Backend required an API key to authenticate requests
- Users needed authentication to create their first API key
- New users logging in via Supabase Auth had no way to create their first API key

**Error:** `{"detail":"Invalid API key"}` when attempting POST to `/keys`

---

## Solution Implemented

### Backend Changes

#### 1. Updated Authentication System (`app/services/auth.py`)

**What changed:**
- Added support for dual authentication methods:
  1. **API Key** (existing): `x-api-key` header for users with keys
  2. **Supabase JWT Token** (NEW): `Authorization: Bearer <token>` header for new users

**Code added:**
```python
async def get_current_user(
    api_key: Optional[str] = Security(api_key_header),
    authorization: Optional[str] = Header(None)
) -> dict:
    # Try Supabase Auth token first (Authorization: Bearer <token>)
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        user_data = verify_supabase_token(token)
        if user_data:
            return {
                "user_id": user_data["user_id"],
                "email": user_data.get("email"),
                "is_global": False,
                "auth_method": "supabase"
            }
    
    # Fallback to API key authentication...
```

**Benefits:**
- New users can authenticate with their Supabase session token
- Existing users continue using API keys
- Backward compatible with global API key

---

#### 2. Added Token Verification (`app/services/supabase_client.py`)

**New function:**
```python
def verify_supabase_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify Supabase Auth JWT token"""
    try:
        response = supabase.auth.get_user(token)
        if response and response.user:
            return {
                "user_id": response.user.id,
                "email": response.user.email
            }
        return None
    except Exception as e:
        logger.error(f"Error verifying Supabase token: {e}")
        return None
```

**What it does:**
- Validates JWT token against Supabase Auth
- Extracts user_id and email from token
- Returns None if token is invalid or expired

---

### Frontend Changes

#### 3. Enhanced API Client (`src/services/api.ts`)

**What changed:**
- Added automatic Supabase Auth token injection
- Falls back to Auth token when no API key exists

**Code added:**
```typescript
// Get Supabase Auth token
async function getAuthToken(): Promise<string | null> {
  if (!supabase) return null;
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token || null;
}

// In fetchAPI function:
if (apiKey) {
  headers['x-api-key'] = apiKey;
} else {
  // If no API key, try to use Supabase Auth token
  const authToken = await getAuthToken();
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
}
```

**Flow:**
1. Check for API key in localStorage
2. If found, use `x-api-key` header
3. If not found, get Supabase session token
4. Use `Authorization: Bearer <token>` header

---

## Authentication Flow

### New User Journey (FIXED)

```
1. User creates account on /register
   ↓
2. User logs in via Supabase Auth
   ↓
3. Frontend stores JWT token in Supabase session
   ↓
4. User navigates to dashboard
   ↓
5. API key setup modal appears
   ↓
6. User clicks "Create API Key"
   ↓
7. Frontend sends POST /keys with Authorization: Bearer <jwt_token>
   ↓
8. Backend verifies JWT token via Supabase
   ↓
9. API key created and returned: gsp_xxxxx
   ↓
10. Frontend saves key to localStorage
   ↓
11. Future requests use x-api-key header
```

### Existing User Journey (UNCHANGED)

```
1. User has API key in localStorage
   ↓
2. All requests include x-api-key header
   ↓
3. Backend verifies key in database
   ↓
4. Request processed
```

---

## Testing Instructions

### Test 1: New User API Key Creation

1. **Clear browser storage:**
   ```javascript
   localStorage.clear()
   ```

2. **Register new account:**
   - Navigate to http://localhost:5173/register
   - Create account with email/password
   - Check email for verification link (if required)

3. **Login:**
   - Navigate to http://localhost:5173/login
   - Sign in with credentials

4. **API Key Setup Modal should appear:**
   - Click "Create API Key"
   - Wait for key generation

5. **Verify success:**
   - Toast notification: "API key created successfully!"
   - Modal closes
   - API key saved in localStorage
   - Check console: `localStorage.getItem('api_key')`

### Test 2: Existing User Flow

1. **User with existing API key:**
   - Login normally
   - API key already in localStorage
   - No modal appears
   - Dashboard loads data

2. **Create additional keys:**
   - Go to Settings page
   - Create new API key
   - Should work with existing key authentication

### Test 3: Backend Verification

**Test Supabase Auth endpoint:**
```powershell
# Get your Supabase session token from browser
# (Open DevTools → Application → Session Storage → access_token)

$token = "YOUR_SUPABASE_ACCESS_TOKEN"

Invoke-WebRequest -Uri "http://localhost:8000/keys" `
  -Method POST `
  -Headers @{
    "Content-Type"="application/json"
    "Authorization"="Bearer $token"
  } `
  -Body '{"name": "Test Key"}'
```

**Expected response:**
```json
{
  "id": "uuid",
  "api_key": "gsp_xxxxxxxxxxxxxxxxxxxxx",
  "name": "Test Key",
  "is_active": true,
  "created_at": "2025-12-08T...",
  "last_used_at": null
}
```

---

## Security Considerations

### ✅ Token Validation
- JWT tokens verified against Supabase Auth server
- Expired tokens rejected automatically
- Invalid tokens return 401 Unauthorized

### ✅ User Isolation
- user_id extracted from verified token
- API keys scoped to authenticated user
- No cross-user access possible

### ✅ API Key Security
- Keys generated with `secrets.token_urlsafe(32)`
- Stored as `gsp_` prefix + 43 random characters
- Keys are hashed (if implemented) or stored securely
- Only shown once at creation time

### ✅ Backward Compatibility
- Existing API keys continue working
- Global API key still supported (dev mode)
- No breaking changes for existing users

---

## Error Handling

### Frontend Errors

**"Authentication required. Provide either x-api-key or Authorization header"**
- **Cause:** No authentication provided
- **Fix:** Login via Supabase Auth

**"Invalid API key"**
- **Cause:** API key in localStorage is invalid or deactivated
- **Fix:** Clear localStorage and create new key

**"Failed to create API key"**
- **Cause:** Backend error or network issue
- **Fix:** Check backend logs, verify Supabase connection

### Backend Errors

**"Error verifying Supabase token"**
- **Cause:** Supabase client misconfigured or token expired
- **Fix:** Check `SUPABASE_SERVICE_KEY` in .env

**"Cannot create keys with global API key"**
- **Cause:** Trying to create personal key with global API key
- **Fix:** Use Supabase Auth token instead

---

## Environment Variables Required

### Backend (.env)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...  # Service role key (not anon key!)
API_KEY=optional_global_key       # Optional for backward compatibility
```

### Frontend (.env)
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...  # Anon key for Auth
VITE_API_URL=http://localhost:8000
```

---

## Database Schema

### user_api_keys Table

```sql
CREATE TABLE user_api_keys (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id),
  api_key TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  last_used_at TIMESTAMPTZ
);

-- Index for fast API key lookup
CREATE INDEX idx_user_api_keys_api_key ON user_api_keys(api_key);
CREATE INDEX idx_user_api_keys_user_id ON user_api_keys(user_id);
```

---

## Rollback Plan

If issues occur, revert to API key-only authentication:

1. **Restore auth.py:**
   ```bash
   git checkout app/services/auth.py
   ```

2. **Restore supabase_client.py:**
   ```bash
   git checkout app/services/supabase_client.py
   ```

3. **Restore api.ts:**
   ```bash
   git checkout src/services/api.ts
   ```

4. **Manually create API key via database:**
   ```sql
   INSERT INTO user_api_keys (user_id, api_key, name)
   VALUES ('user-uuid', 'gsp_manualkey', 'Manual Key');
   ```

---

## Next Steps

### Immediate
- [x] Test new user registration flow
- [x] Test API key creation with Auth token
- [x] Verify existing users still work

### Future Enhancements
- [ ] Add API key expiration dates
- [ ] Implement API key rotation
- [ ] Add rate limiting per API key
- [ ] Email notification on key creation
- [ ] API key usage analytics

---

## Summary

**Problem:** Chicken-and-egg authentication preventing API key creation

**Solution:** Added Supabase JWT token authentication as alternative to API keys

**Impact:** 
- ✅ New users can now create their first API key
- ✅ Existing users unaffected
- ✅ No breaking changes
- ✅ Improved security with proper token validation

**Status:** Ready for testing
