# DEPLOYMENT GUIDE
**Service:** Instant AI Lead Capture  

## 1. Local Docker Deployment
```bash
cp .env.example .env
docker-compose up --build -d
```
The service will boot at `http://localhost:8000`.

## 2. Render / Railway Deployment
1. Connect GitHub repository to Render or Railway dashboard.
2. Set Build Command: `pip install -r requirements.txt`
3. Set Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
4. Inject Environment Variables from `.env.example` (inserting live OpenAI keys).
