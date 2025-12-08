# Quick Migration Checklist ✅

## Step 1: Database Setup (5 minutes)

1. Open Supabase SQL Editor
2. Copy SQL from `API_KEYS_GUIDE.md` (Step 1)
3. Run the SQL migration
4. Verify tables created:
   - `user_api_keys` ✓
   - `threats` has `user_id` column ✓

## Step 2: Backend Restart

```powershell
# Stop if running (Ctrl+C)

# Start backend
cd C:\workspace\backend
uvicorn app.main:app --reload
```

## Step 3: Test New Endpoints

Open http://localhost:8000/docs

You should see new endpoints:
- `POST /keys` - Create API key
- `GET /keys` - List API keys  
- `DELETE /keys/{key_id}` - Deactivate key

## Step 4: Create Your First User API Key

### Option A: Via API (if you have global API_KEY set)

```powershell
$headers = @{
    "x-api-key" = "YOUR_GLOBAL_KEY"
    "Content-Type" = "application/json"
}

$body = @{
    name = "My First Key"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/keys" -Method Post -Headers $headers -Body $body
```

### Option B: Via Supabase Auth + SQL

1. Create a user in Supabase Auth dashboard
2. Get user ID from auth.users table
3. Run SQL:
```sql
INSERT INTO user_api_keys (user_id, api_key, name)
VALUES ('USER_ID_HERE', 'gsp_' || encode(gen_random_bytes(24), 'base64'), 'First Key')
RETURNING *;
```

## Step 5: Test With New Key

```powershell
# Save the api_key from response
$apiKey = "gsp_xxxxx"  # Your new key

# Test analyze
$headers = @{
    "x-api-key" = $apiKey
    "Content-Type" = "application/json"
}

$body = @{
    text = "Click here to verify your bank password!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/analyze" -Method Post -Headers $headers -Body $body

# Test stats
Invoke-RestMethod -Uri "http://localhost:8000/stats" -Headers $headers
```

## Step 6: Integrate with Frontend

Update your frontend to:
1. Use Supabase Auth for user login
2. Call `POST /keys` to create API key on signup
3. Store API key securely
4. Include in all API requests

## ✅ Success Criteria

- [ ] Database tables created
- [ ] Backend restarted without errors
- [ ] New endpoints visible in /docs
- [ ] Can create API key
- [ ] Can analyze with new key
- [ ] Stats returns user-specific data

## 🆘 Troubleshooting

**Error: relation "user_api_keys" does not exist**
→ Run Step 1 SQL migration

**Error: 401 Unauthorized**
→ Check x-api-key header is included

**Error: 403 Forbidden**  
→ API key invalid or deactivated

**No data in stats**
→ First run /analyze to create some data

## 📝 Notes

- Global API_KEY still works (backward compatible)
- Old threats without user_id still accessible
- Each user only sees their own new data
- API keys never expire (unless you set expires_at)

---

**You're all set!** 🎉 Your Guardian Security Platform now has per-user API keys with Supabase Auth integration.
