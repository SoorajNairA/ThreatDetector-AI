# Guardian Security Platform - Quick Start Guide

Get up and running in 5 minutes!

## 🚀 Quick Setup

### 1. Prerequisites Check

```powershell
# Check Python version (need 3.11+)
python --version

# Check pip
pip --version
```

### 2. Install Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 3. Configure Supabase

**Create Table:**

Go to Supabase SQL Editor and run:

```sql
CREATE TABLE threats (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  text TEXT NOT NULL,
  risk_level TEXT NOT NULL,
  risk_score FLOAT NOT NULL,
  intent TEXT,
  ai_generated BOOLEAN,
  actor TEXT,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  style_score FLOAT,
  url_detected BOOLEAN DEFAULT FALSE,
  domains TEXT[],
  keywords TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER PUBLICATION supabase_realtime ADD TABLE threats;
```

### 4. Create Environment File

```powershell
Copy-Item .env.example .env
```

Edit `.env` and add your Supabase credentials:
- `SUPABASE_URL` - From Supabase Settings → API
- `SUPABASE_SERVICE_KEY` - From Supabase Settings → API

### 5. Run Server

```powershell
uvicorn app.main:app --reload
```

### 6. Test It!

Open browser to http://localhost:8000/docs

Or use curl:

```powershell
# Health check
curl http://localhost:8000/health

# Analyze text
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{\"text\": \"Click here to verify your password!\"}'
```

## ✅ Success!

You should see:
- Server running at http://localhost:8000
- API docs at http://localhost:8000/docs
- Threat records appearing in Supabase

## 🐛 Common Issues

**Import errors?**
```powershell
pip install -r requirements.txt
```

**Supabase connection error?**
- Check your URL and key in `.env`
- Verify table exists in Supabase

**Port already in use?**
- Change PORT in `.env` to 8001
- Or kill process: `Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force`

## 🎯 Next Steps

1. Connect your frontend to http://localhost:8000
2. Enable API key auth by setting `API_KEY` in `.env`
3. Check `/stats` endpoint to see aggregate data
4. Review README.md for full documentation
