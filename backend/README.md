# Guardian Security Platform - Backend

Production-ready FastAPI backend for real-time threat detection and analysis. This service provides HTTP APIs for analyzing text content, detecting potential threats, and storing results in Supabase.

## 🎯 Features

- **Threat Analysis API** - POST /analyze endpoint with comprehensive risk scoring
- **Health Monitoring** - GET /health for service health checks
- **Statistics** - GET /stats for aggregate threat metrics
- **Simple Authentication** - Optional API key validation
- **Supabase Integration** - Automatic storage and Realtime support
- **Docker Ready** - Production container with health checks
- **Modular Architecture** - Easy to extend and upgrade classifiers

## 🏗️ Architecture

The backend uses a clean, modular architecture:

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic schemas
│   ├── logging_config.py    # Logging setup
│   ├── routes/              # API endpoints
│   │   ├── analyze.py       # Threat analysis endpoint
│   │   ├── health.py        # Health check endpoint
│   │   └── stats.py         # Statistics endpoint
│   ├── services/            # Business logic
│   │   ├── classifier.py    # Threat classification (UPGRADEABLE)
│   │   ├── supabase_client.py # Database operations
│   │   └── auth.py          # Authentication
│   └── utils/               # Utilities
│       ├── text_features.py # Text analysis utilities
│       └── url_utils.py     # URL detection
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container definition
└── .env.example           # Environment template
```

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.11** or newer
- **pip** package manager
- **Supabase account** with a project created
- **Docker** (optional, for containerized deployment)

## 🚀 Setup Instructions

### Step 1: Clone and Navigate

```bash
cd backend
```

### Step 2: Create Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials:

```env
APP_ENV=dev
API_KEY=                                    # Optional: leave empty for dev
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_THREATS_TABLE=threats
FRONTEND_ORIGIN=http://localhost:3000
PORT=8000
```

**Getting Supabase Credentials:**
1. Go to your Supabase project dashboard
2. Navigate to Settings → API
3. Copy the project URL and service role key

### Step 5: Create Supabase Table

Run this SQL in your Supabase SQL Editor:

```sql
-- Create threats table
CREATE TABLE threats (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  text TEXT NOT NULL,
  risk_level TEXT NOT NULL CHECK (risk_level IN ('HIGH', 'MEDIUM', 'LOW')),
  risk_score FLOAT NOT NULL CHECK (risk_score >= 0 AND risk_score <= 1),
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

-- Create indexes for performance
CREATE INDEX idx_threats_risk_level ON threats(risk_level);
CREATE INDEX idx_threats_timestamp ON threats(timestamp DESC);
CREATE INDEX idx_threats_actor ON threats(actor);

-- Enable Realtime (for frontend auto-updates)
ALTER PUBLICATION supabase_realtime ADD TABLE threats;
```

## 🏃 Running Locally

### Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The server will start at `http://localhost:8000`

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Test the API

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Analyze Text:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Click here to verify your bank account password!"
  }'
```

**Get Statistics:**
```bash
curl http://localhost:8000/stats
```

## 🐳 Running with Docker

### Build the Image

```bash
docker build -t guardian-backend .
```

### Run the Container

```bash
docker run --env-file .env -p 8000:8000 guardian-backend
```

Or with individual environment variables:

```bash
docker run -p 8000:8000 \
  -e SUPABASE_URL=https://your-project.supabase.co \
  -e SUPABASE_SERVICE_KEY=your-key \
  -e FRONTEND_ORIGIN=http://localhost:3000 \
  guardian-backend
```

### Check Container Health

```bash
docker ps
```

The container includes a health check that polls `/health` every 30 seconds.

## 🧪 Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

Run specific test:

```bash
pytest tests/test_health.py
pytest tests/test_analyze_basic.py
```

## 📊 API Reference

### POST /analyze

Analyze text content for threats.

**Request Body:**
```json
{
  "text": "Text to analyze",
  "metadata": {
    "optional": "metadata"
  }
}
```

**Response:**
```json
{
  "risk_level": "HIGH",
  "risk_score": 0.84,
  "analysis": {
    "ai_generated": true,
    "ai_score": 0.7,
    "intent": "phishing",
    "intent_score": 0.9,
    "style_score": 0.6,
    "url_detected": true,
    "url_score": 0.7,
    "keywords": ["click", "verify", "password"],
    "keyword_score": 0.8
  },
  "timestamp": "2025-12-08T10:30:00Z"
}
```

**Risk Levels:**
- `HIGH`: risk_score ≥ 0.8
- `MEDIUM`: risk_score ≥ 0.5
- `LOW`: risk_score < 0.5

**Risk Score Formula:**
```
risk_score = 0.4 × ai_score 
           + 0.3 × intent_score 
           + 0.15 × style_score 
           + 0.1 × url_score 
           + 0.05 × keyword_score
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

### GET /stats

Get aggregate statistics.

**Response:**
```json
{
  "total": 120,
  "high": 19,
  "medium": 45,
  "low": 56,
  "actors": 6,
  "last": "2025-12-08T10:43:12Z"
}
```

## 🔐 Security

### API Key Authentication

Set `API_KEY` in your `.env` file to enable authentication:

```env
API_KEY=your-secret-key-here
```

Include the key in requests:

```bash
curl -H "x-api-key: your-secret-key-here" \
  http://localhost:8000/analyze \
  -d '{"text": "..."}'
```

**Note:** For development, you can leave `API_KEY` empty to disable authentication.

### CORS Configuration

Configure allowed origins via `FRONTEND_ORIGIN`:

```env
FRONTEND_ORIGIN=http://localhost:3000
```

In development mode (`APP_ENV=dev`), CORS is permissive. In production, only specified origins are allowed.

## 🔧 Classifier Implementation

### Current Implementation (Placeholder)

The current classifier uses **lightweight heuristics** for demonstration:

- **AI Detection**: Based on text length and formal tone
- **Intent Classification**: Keyword matching for phishing/spam/scam
- **Stylometry**: Uppercase ratio and sentence length analysis
- **URL Detection**: Regex-based URL extraction
- **Keyword Scoring**: Threat keyword counting

**This is intentionally simple and designed to be upgraded.**

### Upgrading to ML Models

The architecture is modular. To upgrade to ONNX models or hybrid ML:

1. **Install ML dependencies:**
   ```bash
   pip install onnxruntime transformers
   ```

2. **Update `services/classifier.py`:**
   - Replace heuristic functions with ONNX inference
   - Keep the same `analyze_text()` function signature
   - No changes needed to route handlers!

3. **Example upgrade path:**
   ```python
   # services/classifier.py
   import onnxruntime as ort
   
   roberta_session = ort.InferenceSession("models/roberta.onnx")
   
   def compute_ai_score(text: str) -> tuple[bool, float]:
       # Replace heuristic with ONNX inference
       inputs = tokenize(text)
       outputs = roberta_session.run(None, inputs)
       return outputs[0], outputs[1]
   ```

The rest of the application remains unchanged!

## 🔄 Deployment

### Environment Variables for Production

```env
APP_ENV=prod
API_KEY=strong-secret-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_THREATS_TABLE=threats
FRONTEND_ORIGIN=https://your-frontend.com
PORT=8000
```

### Production Checklist

- [ ] Set strong `API_KEY`
- [ ] Use Supabase service role key (not anon key)
- [ ] Configure proper `FRONTEND_ORIGIN`
- [ ] Set `APP_ENV=prod`
- [ ] Enable HTTPS
- [ ] Set up monitoring and logging
- [ ] Configure auto-scaling (if needed)

### Render Deployment

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from Render dashboard
6. Deploy!

### Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

## 📈 Monitoring

The application logs key events:

```
2025-12-08 10:30:00 - app.main - INFO - Guardian Security Platform - Starting Up
2025-12-08 10:30:05 - app.services.classifier - INFO - Analyzing text of length 142
2025-12-08 10:30:05 - app.services.classifier - INFO - Analysis complete: risk_level=HIGH, risk_score=0.84
2025-12-08 10:30:05 - app.services.supabase_client - INFO - Inserting threat record into Supabase
```

Monitor logs in production:

```bash
# Docker logs
docker logs -f <container-id>

# Render logs
# Check Logs tab in Render dashboard
```

## 🛠️ Troubleshooting

### "Connection refused" error

- Check if server is running: `curl http://localhost:8000/health`
- Verify port is not in use: `netstat -an | findstr :8000` (Windows)

### Supabase connection errors

- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are correct
- Check network connectivity
- Ensure service role key (not anon key) is used

### Tests failing

- Ensure virtual environment is activated
- Install dev dependencies: `pip install pytest pytest-asyncio`
- Check Supabase credentials in `.env`

### Docker build issues

- Ensure Dockerfile is in `backend/` directory
- Check Docker daemon is running
- Try with `--no-cache`: `docker build --no-cache -t guardian-backend .`

## 🤝 Contributing

The codebase follows these principles:

- **Modular**: Each component has a single responsibility
- **Extensible**: Easy to upgrade classifiers without touching routes
- **Testable**: Comprehensive test coverage
- **Documented**: Clear docstrings and comments

## 📝 Notes

- The current classifier is a **placeholder** using simple heuristics
- Designed for easy upgrade to ONNX models or hybrid ML
- No external LLM API calls - all processing is local
- Supabase Realtime automatically notifies frontend of new threats
- API responses are stable - frontend can rely on schema

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check Supabase logs
4. Review application logs

---

**Built with FastAPI, Supabase, and Docker** 🚀
