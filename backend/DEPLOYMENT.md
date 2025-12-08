# Deployment Guide - Guardian Security Platform

Complete deployment instructions for multiple platforms.

## 🎯 Prerequisites

- Backend code ready
- Supabase project created and configured
- Environment variables prepared

## 📋 Pre-Deployment Checklist

- [ ] All tests passing: `pytest`
- [ ] Environment variables documented
- [ ] Supabase table created
- [ ] API documentation reviewed at `/docs`
- [ ] Docker image builds successfully (if using Docker)

---

## 🚀 Deployment Options

### Option 1: Render (Recommended for Quick Deploy)

**Render** is a PaaS with free tier and easy deployment.

#### Steps:

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Create Web Service on Render**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure Service**
   - **Name**: guardian-backend
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or paid for production)

4. **Set Environment Variables**
   In Render dashboard, add:
   ```
   APP_ENV=prod
   API_KEY=your-secret-key
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_KEY=your-service-role-key
   SUPABASE_THREATS_TABLE=threats
   FRONTEND_ORIGIN=https://your-frontend.com
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build and deployment (~2-3 minutes)
   - Service will be live at `https://your-app.onrender.com`

6. **Verify**
   ```bash
   curl https://your-app.onrender.com/health
   ```

#### Render Configuration File

Create `render.yaml` in project root:

```yaml
services:
  - type: web
    name: guardian-backend
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: APP_ENV
        value: prod
      - key: API_KEY
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: SUPABASE_THREATS_TABLE
        value: threats
      - key: FRONTEND_ORIGIN
        sync: false
```

---

### Option 2: Docker + Any Cloud

Deploy containerized app to any platform supporting Docker.

#### Build Image

```bash
cd backend
docker build -t guardian-backend:latest .
```

#### Test Locally

```bash
docker run --env-file .env -p 8000:8000 guardian-backend:latest
```

#### Push to Registry

**Docker Hub:**
```bash
docker login
docker tag guardian-backend:latest yourusername/guardian-backend:latest
docker push yourusername/guardian-backend:latest
```

**AWS ECR:**
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag guardian-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/guardian-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/guardian-backend:latest
```

#### Deploy to Cloud

**AWS ECS:**
- Create ECS cluster
- Create task definition with image
- Set environment variables in task definition
- Create service with desired count

**Google Cloud Run:**
```bash
gcloud run deploy guardian-backend \
  --image gcr.io/project-id/guardian-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Azure Container Instances:**
```bash
az container create \
  --resource-group myResourceGroup \
  --name guardian-backend \
  --image yourusername/guardian-backend:latest \
  --dns-name-label guardian-backend \
  --ports 8000 \
  --environment-variables \
    APP_ENV=prod \
    SUPABASE_URL=<url> \
    SUPABASE_SERVICE_KEY=<key>
```

---

### Option 3: Heroku

**Note**: Heroku ended free tier. Consider Render instead.

#### Steps:

1. **Install Heroku CLI**
   ```bash
   # Windows
   choco install heroku-cli
   
   # macOS
   brew install heroku/brew/heroku
   ```

2. **Login and Create App**
   ```bash
   heroku login
   heroku create guardian-backend
   ```

3. **Add Buildpack**
   ```bash
   heroku buildpacks:set heroku/python
   ```

4. **Create Procfile**
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

5. **Set Environment Variables**
   ```bash
   heroku config:set APP_ENV=prod
   heroku config:set API_KEY=your-key
   heroku config:set SUPABASE_URL=your-url
   heroku config:set SUPABASE_SERVICE_KEY=your-key
   ```

6. **Deploy**
   ```bash
   git push heroku main
   ```

---

### Option 4: Railway

Similar to Render, Railway is modern PaaS.

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Railway auto-detects Python
5. Add environment variables in dashboard
6. Deploy automatically

---

### Option 5: DigitalOcean App Platform

1. Go to DigitalOcean App Platform
2. Create new app from GitHub
3. Select repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
5. Add environment variables
6. Deploy

---

### Option 6: Fly.io

1. **Install flyctl**
   ```bash
   # Windows
   iwr https://fly.io/install.ps1 -useb | iex
   
   # macOS
   brew install flyctl
   ```

2. **Login and Initialize**
   ```bash
   fly auth login
   fly launch
   ```

3. **Configure fly.toml**
   ```toml
   app = "guardian-backend"
   
   [build]
     dockerfile = "Dockerfile"
   
   [[services]]
     internal_port = 8000
     protocol = "tcp"
   
     [[services.ports]]
       handlers = ["http"]
       port = 80
   
     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   ```

4. **Set Secrets**
   ```bash
   fly secrets set API_KEY=your-key
   fly secrets set SUPABASE_URL=your-url
   fly secrets set SUPABASE_SERVICE_KEY=your-key
   ```

5. **Deploy**
   ```bash
   fly deploy
   ```

---

## 🔧 Environment Variables Reference

**Required:**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_KEY` - Supabase service role key

**Optional:**
- `APP_ENV` - Environment (dev/prod)
- `API_KEY` - Backend API key for authentication
- `SUPABASE_THREATS_TABLE` - Table name (default: threats)
- `FRONTEND_ORIGIN` - CORS origin
- `PORT` - Server port (default: 8000)

---

## 🔍 Post-Deployment Verification

### 1. Health Check
```bash
curl https://your-app-url.com/health
# Expected: {"status": "ok"}
```

### 2. Test Analysis
```bash
curl -X POST https://your-app-url.com/analyze \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-key" \
  -d '{"text": "Click here to verify your password"}'
```

### 3. Check Stats
```bash
curl https://your-app-url.com/stats \
  -H "x-api-key: your-key"
```

### 4. API Documentation
Visit: `https://your-app-url.com/docs`

---

## 📊 Monitoring and Logging

### Application Logs

**Render:**
- Go to service dashboard → Logs tab

**Docker:**
```bash
docker logs <container-id> -f
```

**Heroku:**
```bash
heroku logs --tail
```

**AWS CloudWatch:**
- Automatic with ECS/Lambda

### Health Monitoring

Set up monitoring service to poll `/health`:

**UptimeRobot** (Free):
1. Go to uptimerobot.com
2. Add HTTP monitor
3. URL: `https://your-app-url.com/health`
4. Interval: 5 minutes

**Pingdom**, **Better Uptime**, etc. work similarly.

### Error Tracking

**Sentry Integration:**

```bash
pip install sentry-sdk[fastapi]
```

```python
# In app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

---

## 🚨 Troubleshooting

### Build Fails

**Error**: `requirements.txt not found`
- Ensure file is in repository root
- Check file name spelling

**Error**: `Python version mismatch`
- Add `runtime.txt` with `python-3.11`

### Deployment Succeeds but App Crashes

**Check logs** for:
- Missing environment variables
- Supabase connection errors
- Port binding issues

**Fix**:
```bash
# Verify env vars are set
# Check logs for specific error
# Ensure PORT is bound correctly
```

### CORS Errors

**Error**: `Access-Control-Allow-Origin`

**Fix**:
```env
FRONTEND_ORIGIN=https://your-actual-frontend.com
```

### Supabase Connection Timeout

**Check**:
- Service role key is correct (not anon key)
- Supabase URL is correct
- No firewall blocking outbound connections

---

## 🔒 Security Best Practices

### Production Checklist

- [ ] Strong API_KEY set (use password generator)
- [ ] SUPABASE_SERVICE_KEY is service role, not anon
- [ ] APP_ENV=prod
- [ ] FRONTEND_ORIGIN set to actual domain
- [ ] HTTPS enabled (automatic on most platforms)
- [ ] Secrets not in version control
- [ ] Regular dependency updates
- [ ] Logging configured
- [ ] Monitoring alerts set up

### Secrets Management

**Don't:**
- Commit .env to git
- Share secrets in chat/email
- Use same secrets for dev/prod

**Do:**
- Use platform secret management
- Rotate keys periodically
- Use different keys per environment
- Document which keys are active

---

## 📈 Scaling

### Horizontal Scaling

Most platforms support auto-scaling:

**Render**: Scale in dashboard
**Heroku**: `heroku ps:scale web=3`
**Docker**: Use orchestration (K8s, ECS, Swarm)

### Performance Optimization

1. **Database Connection Pooling**
   - Supabase handles this
   
2. **Caching**
   - Add Redis for frequent queries
   
3. **Load Balancing**
   - Automatic on most platforms
   
4. **CDN**
   - For static assets (if added later)

---

## 💰 Cost Estimates

### Free Tier Options

- **Render**: Free (with limitations)
- **Railway**: $5 credit/month
- **Fly.io**: Free allowance
- **Supabase**: Free tier generous

### Paid Estimates (Monthly)

- **Render**: $7-25 for small apps
- **Heroku**: $7-25 for hobby/professional
- **AWS**: $10-50 (varies greatly)
- **DigitalOcean**: $5-12 for basic droplet

### Recommended for Production

- **Small**: Render ($7) + Supabase Free
- **Medium**: DigitalOcean ($12) + Supabase Pro ($25)
- **Large**: AWS ECS + RDS

---

## 🎓 Additional Resources

- [Render Docs](https://render.com/docs)
- [Docker Docs](https://docs.docker.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Supabase Edge Functions](https://supabase.com/docs/guides/functions)

---

## ✅ Success!

Your Guardian Security Platform backend is now deployed and ready to protect! 🛡️

**Next**: Connect your frontend to the deployed API URL.
