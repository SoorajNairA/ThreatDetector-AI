# Per-User API Keys with Supabase Auth - Complete Guide

## 🎯 Overview

Your Guardian Security Platform now supports:
- ✅ **Per-user API keys** - Each user gets their own unique API keys
- ✅ **Supabase Auth integration** - User authentication via Supabase
- ✅ **API key management** - Create, list, and deactivate keys
- ✅ **User-scoped data** - Each user only sees their own threats
- ✅ **Backward compatibility** - Global API key still works

## 📋 Setup Steps

### Step 1: Run Database Migration

Execute this SQL in your Supabase SQL Editor:

```sql
-- Table to store user API keys
CREATE TABLE user_api_keys (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  api_key TEXT NOT NULL UNIQUE,
  name TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_used_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_user_api_keys_api_key ON user_api_keys(api_key) WHERE is_active = TRUE;
CREATE INDEX idx_user_api_keys_user_id ON user_api_keys(user_id);

-- Update threats table
ALTER TABLE threats ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL;
CREATE INDEX idx_threats_user_id ON threats(user_id);

-- Enable RLS
ALTER TABLE user_api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE threats ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_api_keys
CREATE POLICY "Users can view their own API keys"
  ON user_api_keys FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own API keys"
  ON user_api_keys FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own API keys"
  ON user_api_keys FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Service role can do everything"
  ON user_api_keys FOR ALL
  USING (auth.role() = 'service_role');

-- RLS Policies for threats
CREATE POLICY "Users can view their own threats"
  ON threats FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Service role can insert threats"
  ON threats FOR INSERT
  WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role can view all threats"
  ON threats FOR SELECT
  USING (auth.role() = 'service_role');
```

### Step 2: Restart Backend

```powershell
# If running locally
uvicorn app.main:app --reload
```

### Step 3: Test the New Endpoints

Visit http://localhost:8000/docs to see the new API key management endpoints.

## 🔑 API Key Management

### Create New API Key

**Endpoint:** `POST /keys`

**Headers:**
```
x-api-key: your-existing-key  # Or use Supabase Auth token
```

**Request:**
```json
{
  "name": "My Production Key"
}
```

**Response:**
```json
{
  "id": "uuid",
  "api_key": "gsp_xxxxxxxxxxxxxxxxxxxxxxxxxxx",  // ⚠️ SAVE THIS! Only shown once
  "name": "My Production Key",
  "is_active": true,
  "created_at": "2025-12-08T10:30:00Z",
  "last_used_at": null
}
```

**⚠️ Important:** The `api_key` value is only returned once. Save it securely!

### List Your API Keys

**Endpoint:** `GET /keys`

**Headers:**
```
x-api-key: your-key
```

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "My Production Key",
    "is_active": true,
    "created_at": "2025-12-08T10:30:00Z",
    "last_used_at": "2025-12-08T11:00:00Z"
  }
]
```

Note: API key values are NOT returned (security).

### Deactivate API Key

**Endpoint:** `DELETE /keys/{key_id}`

**Headers:**
```
x-api-key: your-key
```

**Response:**
```json
{
  "message": "API key deactivated successfully"
}
```

## 🔐 Authentication Flow

### Option 1: Using API Keys (Recommended for API clients)

```bash
# Analyze text with your API key
curl -X POST http://localhost:8000/analyze \
  -H "x-api-key: gsp_xxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{"text": "Suspicious message here"}'
```

### Option 2: Using Supabase Auth (For frontend apps)

1. **User signs up/logs in via Supabase Auth:**

```javascript
// Frontend code
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'password'
})

const user = data.user
```

2. **Create API key for user:**

```javascript
// Call your backend to create API key
const response = await fetch('http://localhost:8000/keys', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': 'temporary-global-key' // Or use Supabase session token
  },
  body: JSON.stringify({
    name: 'Web App Key'
  })
})

const { api_key } = await response.json()
// Save api_key securely (e.g., localStorage or secure cookie)
```

3. **Use API key for subsequent requests:**

```javascript
const analysis = await fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': api_key
  },
  body: JSON.stringify({
    text: 'Message to analyze'
  })
})
```

## 📊 User-Scoped Data

### Each User's Data is Isolated

When a user makes a request with their API key:

**Analyze:**
- Threat is stored with their `user_id`
- Only they can see it

**Stats:**
- Returns only their threats
- Counts are user-specific

**Example:**

```bash
# User A's stats
curl -H "x-api-key: user-a-key" http://localhost:8000/stats
# Returns: {"total": 10, "high": 2, ...}

# User B's stats
curl -H "x-api-key: user-b-key" http://localhost:8000/stats
# Returns: {"total": 5, "high": 1, ...}
```

## 🔄 Migration Path

### For Existing Users

If you already have the backend running:

1. **Existing data won't have user_id** - that's okay!
2. **Global API key still works** - backward compatible
3. **New users get per-user keys** - modern approach
4. **Migrate gradually** - both systems work together

### Creating First User API Key

You have two options:

**Option A: Manual SQL Insert**

```sql
-- Get user ID from Supabase Auth
SELECT id FROM auth.users WHERE email = 'user@example.com';

-- Insert API key
INSERT INTO user_api_keys (user_id, api_key, name)
VALUES ('user-uuid-here', 'gsp_manual_key_here', 'Manual Key');
```

**Option B: Via API (Requires global key first)**

```bash
# Set global API key in .env
API_KEY=temp-global-key

# User signs up via Supabase
# Then create their API key via your backend
curl -X POST http://localhost:8000/keys \
  -H "x-api-key: temp-global-key" \
  -H "Content-Type: application/json" \
  -d '{"name": "First Key"}'
```

## 🔒 Security Best Practices

### API Key Format

Keys are generated as: `gsp_` + 32 random bytes (base64)

Example: `gsp_xK9mPqR7sT3wV8yB2nF5jL1hG4dC6eA0`

- **Prefix** identifies them as Guardian Security Platform keys
- **Random** - cryptographically secure
- **Unique** - collision-resistant

### Storage

**Backend:**
- ✅ Plain text in database (lookup required)
- ✅ Updated last_used_at on each use
- ✅ Can be deactivated without deletion

**Frontend:**
- ✅ Store in localStorage or secure cookie
- ✅ Never commit to git
- ✅ Include in .gitignore

### Rotation

```javascript
// Create new key
const newKey = await createAPIKey('Rotated Key')

// Update frontend to use new key
localStorage.setItem('api_key', newKey.api_key)

// Deactivate old key
await deleteAPIKey(oldKeyId)
```

## 📱 Frontend Integration

### React Example

```javascript
// hooks/useAuth.js
export function useAuth() {
  const [apiKey, setApiKey] = useState(localStorage.getItem('api_key'))
  
  const createKey = async (name) => {
    const res = await fetch('/keys', {
      method: 'POST',
      headers: { 'x-api-key': apiKey },
      body: JSON.stringify({ name })
    })
    const data = await res.json()
    return data.api_key
  }
  
  return { apiKey, setApiKey, createKey }
}

// components/Analyzer.jsx
function Analyzer() {
  const { apiKey } = useAuth()
  
  const analyzeText = async (text) => {
    const res = await fetch('/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey
      },
      body: JSON.stringify({ text })
    })
    return res.json()
  }
  
  return <TextInput onSubmit={analyzeText} />
}
```

## 🧪 Testing

### Test API Key Creation

```bash
# Health check (no auth)
curl http://localhost:8000/health

# Create key (with global key)
curl -X POST http://localhost:8000/keys \
  -H "x-api-key: YOUR_GLOBAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Key"}'

# Save the returned api_key value

# Test analyze with new key
curl -X POST http://localhost:8000/analyze \
  -H "x-api-key: gsp_xxxxx" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test message"}'

# Check stats
curl -H "x-api-key: gsp_xxxxx" http://localhost:8000/stats
```

## 🚀 Deployment Notes

### Environment Variables

Your `.env` should have:

```env
# Global API key (optional, for backward compatibility)
API_KEY=optional-global-key

# Supabase (required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

### Supabase Auth Setup

1. Go to Supabase Dashboard → Authentication
2. Enable email auth (or other providers)
3. Configure redirect URLs
4. Users can sign up and get API keys

## 📊 Database Schema

### user_api_keys Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to auth.users |
| api_key | TEXT | The actual API key (unique) |
| name | TEXT | User-friendly name |
| is_active | BOOLEAN | Active/deactivated |
| created_at | TIMESTAMPTZ | Creation timestamp |
| last_used_at | TIMESTAMPTZ | Last usage timestamp |
| expires_at | TIMESTAMPTZ | Optional expiration |

### threats Table (Updated)

Added:
- `user_id` - Links threat to user

## ✅ Summary

You now have:
- ✅ Per-user API key system
- ✅ Supabase Auth integration ready
- ✅ API key management endpoints
- ✅ User data isolation
- ✅ Backward compatibility
- ✅ Secure key generation
- ✅ Usage tracking

**Next steps:**
1. Run the SQL migration
2. Restart your backend
3. Test key creation at `/docs`
4. Integrate with your frontend
5. Deploy! 🚀
