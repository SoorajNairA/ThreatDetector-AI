# Guard Security Platform - SIH 2025 Submission

**Team Name:** .cypher  
**Problem Statement ID:** SIH25161  
**Team ID:** 109414

## Problem Statement

Develop an AI-powered threat detection system capable of identifying phishing, scams, spam, and malicious content in real-time across multiple communication channels.

## Solution Overview

Guard Security Platform is a comprehensive threat detection solution using multi-classifier AI to analyze and classify potential threats with:
- 5 specialized AI classifiers working in ensemble
- Real-time dashboard for threat monitoring
- Encryption-first architecture for data privacy
- RESTful API for seamless integration
- Python SDK for developers
- Online learning for continuous improvement

## Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.9+)
- **Database:** Supabase (PostgreSQL)
- **ML/AI:** TensorFlow, scikit-learn, ONNX Runtime
- **Security:** AES-128-GCM encryption, bcrypt hashing

### Frontend
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **UI Library:** shadcn/ui (Radix UI + Tailwind CSS)
- **Charts:** Recharts
- **Routing:** React Router

### Infrastructure
- **Deployment:** Railway/Render (Backend), Vercel (Frontend)
- **Authentication:** Supabase Auth + JWT
- **Real-time:** Supabase Realtime subscriptions

## Key Features

1. **Multi-Classifier Threat Detection**
   - AI-Generated Text Detection (ONNX model)
   - Intent Classification (Hybrid ML: TF-IDF + Logistic + MiniLM + Rules)
   - Stylometry Analysis (Writing pattern detection)
   - URL Detection & Reputation Check
   - Keyword Matching (1000+ threat keywords)

2. **Security & Privacy**
   - Per-account AES-128-GCM encryption
   - Master key wrapping for key management
   - Bcrypt API key hashing
   - Row-level security (Supabase RLS)
   - Secure credential storage

3. **Real-time Dashboard**
   - Live threat monitoring
   - Interactive analytics & visualizations
   - Threat heatmaps & timelines
   - Risk scoring & classification
   - Historical data analysis

4. **Developer Integration**
   - RESTful API with OpenAPI docs
   - Official Python SDK
   - Batch processing support
   - Webhook notifications (planned)

5. **Online Learning**
   - Continuous model improvement
   - User feedback integration
   - Automated retraining pipeline
   - Privacy-preserving training (consent-based)

## Project Structure

```
.cypher_SIH25161/
├── project/
│   ├── backend/          # FastAPI backend service
│   ├── frontend/         # React dashboard
│   ├── sdk/              # Python SDK with examples
│   ├── assets/           # Diagrams, mockups, sample data
│   ├── scripts/          # Setup & utility scripts
│   └── README.md
├── README.md             # This file
└── team_info.txt         # Team information
```

## Local Development Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Supabase account (free tier)

### Step 1: Backend Setup

```bash
# Navigate to backend directory
cd project/backend

# Create and activate virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env file with your Supabase credentials:
#   SUPABASE_URL=your_supabase_project_url
#   SUPABASE_SERVICE_KEY=your_service_role_jwt_token

# Run database migrations
# Open Supabase SQL Editor and execute migrations in order:
# 1. migrations/001_accounts_encryption.sql
# 2. migrations/002_online_learning.sql
# 3. migrations/003_privacy_training_consent.sql
# 4. migrations/004_add_confidence_columns.sql

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend URLs:**
- API Server: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Interactive API: `http://localhost:8000/redoc`

### Step 2: Frontend Setup

```bash
# Open new terminal and navigate to frontend directory
cd project/frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Edit .env file:
#   VITE_API_URL=http://localhost:8000
#   VITE_SUPABASE_URL=your_supabase_project_url
#   VITE_SUPABASE_ANON_KEY=your_anon_jwt_token

# Start development server
npm run dev
```

**Frontend URL:** `http://localhost:8080`

### Step 3: SDK Setup (Optional)

```bash
# Navigate to SDK directory
cd project/sdk

# Install SDK in development mode
pip install -e .

# Run example chatbot simulator
cd examples
python chatbot_simulator.py
```

### Complete Local Deployment Script

**For Windows (PowerShell):**
```powershell
# Terminal 1 - Backend
cd C:\path\to\.cypher_SIH25161\project\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend (open new terminal)
cd C:\path\to\.cypher_SIH25161\project\frontend
npm install
npm run dev
```

**For Linux/Mac (Bash):**
```bash
# Terminal 1 - Backend
cd /path/to/.cypher_SIH25161/project/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend (open new terminal)
cd /path/to/.cypher_SIH25161/project/frontend
npm install
npm run dev
```

### Verifying Installation

After running both terminals, verify:
1. Backend API: Open `http://localhost:8000/docs` - should show Swagger UI
2. Frontend App: Open `http://localhost:8080` - should show landing page
3. Check terminal outputs for any errors

### Stopping the Application

- **Backend:** Press `Ctrl+C` in backend terminal, then run `deactivate`
- **Frontend:** Press `Ctrl+C` in frontend terminal

## Environment Variables

### Backend (.env)
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_service_role_jwt_token
SUPABASE_THREATS_TABLE=threats
FRONTEND_ORIGIN=http://localhost:3000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_anon_jwt_token
```

## API Usage

### Analyze Text
```bash
POST /analyze
Content-Type: application/json
x-api-key: your_api_key

{
  "text": "Click here to verify your account immediately!"
}
```

**Response:**
```json
{
  "risk_level": "HIGH",
  "risk_score": 0.87,
  "intent": "phishing",
  "intent_confidence": 0.92,
  "ai_generated": true,
  "ai_confidence": 0.89,
  "url_detected": false,
  "keywords": ["click", "verify", "account", "immediately"],
  "timestamp": "2025-12-12T10:30:00Z"
}
```

### Get Statistics
```bash
GET /stats
x-api-key: your_api_key
```

**Response:**
```json
{
  "total": 1247,
  "high": 156,
  "medium": 342,
  "low": 749,
  "actors": 89,
  "last": "2025-12-12T10:30:00Z"
}
```

## Classifier Pipeline

The system uses an ensemble of 5 classifiers with weighted scoring:

1. **AI Classifier (35%)** - Detects AI-generated content
2. **Intent Classifier (35%)** - Identifies threat intent (phishing/scam/spam)
3. **Stylometry (10%)** - Analyzes writing patterns
4. **URL Checker (12%)** - Detects malicious URLs
5. **Keywords (8%)** - Matches threat keywords

**Risk Score Formula:**
```
risk_score = Σ(classifier_score × weight)
```

**Risk Levels:**
- HIGH: risk_score ≥ 0.7
- MEDIUM: 0.4 ≤ risk_score < 0.7
- LOW: risk_score < 0.4

## Testing

### Run Chatbot Simulator
```bash
cd project/sdk/examples
python chatbot_simulator.py
```

**Simulator includes 15 threat scenarios:**
- Phishing attacks
- Prize scams
- Tech support scams
- Romance scams
- Cryptocurrency scams
- Tax/IRS scams
- Rental scams
- Blackmail/extortion
- And more...

### Run Backend Tests
```bash
cd project/backend

# With virtual environment activated
pytest tests/ -v
```

### Manual Testing via Dashboard
1. Open frontend at `http://localhost:5173`
2. Register/login with Supabase credentials
3. Navigate to "Analyze Text" section
4. Enter test messages from `sdk/examples/test_messages.txt`
5. View results in real-time dashboard

## Architecture Diagrams

See `project/assets/diagrams/` for:
- System architecture diagram
- Data flow diagram
- Classifier pipeline diagram
- Security architecture

## Future Enhancements

- [ ] Multi-language support
- [ ] Image/video content analysis
- [ ] Mobile SDK (iOS/Android)
- [ ] Chrome extension
- [ ] Slack/Discord integrations
- [ ] Advanced threat intelligence feeds
- [ ] Custom model training interface

## Team Members

See `team_info.txt` for complete team details.

## License

This project is submitted for Smart India Hackathon 2025.

## Support & Documentation

- API Documentation: `/docs` endpoint
- Project README: `project/README.md`
- Backend README: `project/backend/README.md`
- Frontend README: `project/frontend/README.md`
- SDK Examples: `project/sdk/examples/`

---

**Developed by Team .cypher for SIH 2025**  
**Problem Statement: SIH25161**
