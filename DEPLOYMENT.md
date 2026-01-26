# Research Search Engine - Full Stack Deployment Guide

## 🚀 Complete Working Website Setup

### Architecture
- **Frontend**: React app (localhost:3000 in dev)
- **Backend**: FastAPI (localhost:8000 in dev)
- **Database**: SQLite (papers.db) - contains all research papers

---

## 📦 Local Development

### 1. Backend Setup

```bash
# Install Python dependencies
uv sync

# Start FastAPI backend
uv run uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if not already done)
npm install

# Start React dev server
npm start
```

Frontend will open at: http://localhost:3000

### 3. Database

The papers.db file contains all your research papers. It's already configured and ready to use.

---

## 🌐 Production Deployment

### Option 1: Vercel (Frontend) + Render/Railway (Backend) [RECOMMENDED]

#### Frontend (Vercel - FREE)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Vercel**
   - Go to https://vercel.com
   - Sign in with GitHub
   - Click "New Project"
   - Import your repository
   - Set build settings:
     - Framework Preset: Create React App
     - Root Directory: `frontend`
     - Build Command: `npm run build`
     - Output Directory: `build`
   - Add Environment Variable:
     - `REACT_APP_API_URL` = `https://your-backend-url.onrender.com` (fill this after deploying backend)
   - Click "Deploy"

#### Backend (Render.com - FREE tier available)

1. **Go to https://render.com** and sign up

2. **Create New Web Service**
   - Connect your GitHub repository
   - Settings:
     - Name: `research-search-api`
     - Environment: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - Plan: Free

3. **Upload Database**
   - In Render dashboard, go to your service
   - Navigate to "Disk" or use environment variables
   - Upload `papers.db` to the deployment

4. **Get your backend URL**
   - Copy the URL (e.g., https://research-search-api.onrender.com)
   - Update your Vercel frontend environment variable `REACT_APP_API_URL` with this URL

---

### Option 2: Railway.app (Full Stack) [RECOMMENDED FOR SIMPLICITY]

Railway can host both frontend and backend together.

1. **Go to https://railway.app** and sign up

2. **Deploy Backend**
   - Click "New Project" → "Deploy from GitHub"
   - Select your repository
   - Railway will auto-detect Python
   - Add environment variables if needed
   - Upload `papers.db` via volume mount

3. **Deploy Frontend**
   - Add a new service to the same project
   - Point to `frontend` directory
   - Set build command: `npm run build`
   - Set start command: `npx serve -s build`

---

### Option 3: Heroku (Full Stack)

#### Backend Deployment

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create new app
heroku create research-search-api

# Add buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main

# Upload database (use Heroku CLI or dashboard)
```

#### Frontend Deployment

```bash
cd frontend

# Build the app
npm run build

# Deploy to Heroku or use the backend to serve static files
```

---

## 🔧 Configuration Files Created

### Backend
- `requirements.txt` - Python dependencies
- `Procfile` - Heroku/Railway deployment config
- `app/main.py` - Updated with CORS for production

### Frontend
- `.env.local` - Local development API URL
- `.env.production` - Production API URL (update before deploying)
- `package.json` - Updated with proxy and build configs

---

## 🧪 Testing Locally

1. **Start Backend**: `uv run uvicorn app.main:app --reload --port 8000`
2. **Start Frontend**: `cd frontend && npm start`
3. **Open Browser**: http://localhost:3000
4. **Test Search**: Search for "machine learning" or any query

---

## 📝 Important Notes

### Database (papers.db)
- ✅ Keep it in the root directory
- ✅ For production, upload it to your hosting service
- ✅ Consider backing it up regularly
- ⚠️ SQLite has limitations for high-traffic sites (consider PostgreSQL for production)

### CORS Configuration
- Already configured in `app/main.py`
- Allows requests from localhost:3000 (dev) and Vercel domains (prod)
- Update `allow_origins` if you deploy to a different domain

### Environment Variables
- Frontend: `.env.local` (dev), `.env.production` (prod)
- Backend: No env vars needed for basic setup

---

## 🎉 Next Steps

1. ✅ Test locally to ensure everything works
2. ✅ Push to GitHub
3. ✅ Deploy backend to Render/Railway/Heroku
4. ✅ Deploy frontend to Vercel
5. ✅ Update frontend API URL with backend URL
6. ✅ Test production deployment

---

## 🆘 Troubleshooting

### CORS Errors
- Make sure backend CORS allows your frontend domain
- Check `app/main.py` CORS configuration

### API Not Found
- Verify `REACT_APP_API_URL` is set correctly
- Check backend is running and accessible

### Database Errors
- Ensure `papers.db` is in the correct location
- Check file permissions

---

## 💡 Free Hosting Summary

| Service | Frontend | Backend | Database | Free Tier |
|---------|----------|---------|----------|-----------|
| **Vercel** | ✅ | ❌ | ❌ | Unlimited |
| **Render** | ✅ | ✅ | ⚠️ (Limited) | 750 hrs/month |
| **Railway** | ✅ | ✅ | ✅ | $5 free/month |
| **Heroku** | ✅ | ✅ | ⚠️ (Limited) | Dyno hours |

**Recommended**: Vercel (Frontend) + Render (Backend)

---

Good luck with your deployment! 🚀
